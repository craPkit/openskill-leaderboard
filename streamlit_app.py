import streamlit as st

# Import our modules
from models import initialize_data, add_player, get_all_players, record_match, save_data, load_data
from rating_system import update_ratings, get_leaderboard
from utils import get_player_stats, get_recent_matches, get_most_frequent_teammates

# Page configuration
st.set_page_config(
    page_title="Table Soccer Tracker",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize data
initialize_data()
load_data()

# Initialize session state for match setup
if 'team1_player1' not in st.session_state:
    st.session_state.team1_player1 = None
if 'team1_player2' not in st.session_state:
    st.session_state.team1_player2 = None
if 'team2_player1' not in st.session_state:
    st.session_state.team2_player1 = None
if 'team2_player2' not in st.session_state:
    st.session_state.team2_player2 = None
if 'match_setup_mode' not in st.session_state:
    st.session_state.match_setup_mode = False

# App title
st.title("⚽ Table Soccer Tracker")

# Tabs for different sections
tab1, tab2, tab3 = st.tabs(["Play Match", "Leaderboard", "Player Management"])

with tab1:
    st.header("Play Match")

    # Match setup section
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Team 1")

        # Display current team 1 players or buttons to select
        if st.session_state.match_setup_mode:
            if st.session_state.team1_player1 is None:
                if st.button("Select Team 1 - Player 1", key="t1p1_btn", use_container_width=True):
                    st.session_state.selecting_position = "team1_player1"
            else:
                st.info(f"Player 1: {st.session_state.team1_player1}")

            if st.session_state.team1_player2 is None:
                if st.button("Select Team 1 - Player 2", key="t1p2_btn", use_container_width=True):
                    st.session_state.selecting_position = "team1_player2"
            else:
                st.info(f"Player 2: {st.session_state.team1_player2}")
        else:
            if st.session_state.team1_player1 and st.session_state.team1_player2:
                st.success(f"**{st.session_state.team1_player1}** & **{st.session_state.team1_player2}**")
            else:
                st.info("No players selected")

    with col2:
        st.subheader("Team 2")

        # Display current team 2 players or buttons to select
        if st.session_state.match_setup_mode:
            if st.session_state.team2_player1 is None:
                if st.button("Select Team 2 - Player 1", key="t2p1_btn", use_container_width=True):
                    st.session_state.selecting_position = "team2_player1"
            else:
                st.info(f"Player 1: {st.session_state.team2_player1}")

            if st.session_state.team2_player2 is None:
                if st.button("Select Team 2 - Player 2", key="t2p2_btn", use_container_width=True):
                    st.session_state.selecting_position = "team2_player2"
            else:
                st.info(f"Player 2: {st.session_state.team2_player2}")
        else:
            if st.session_state.team2_player1 and st.session_state.team2_player2:
                st.success(f"**{st.session_state.team2_player1}** & **{st.session_state.team2_player2}**")
            else:
                st.info("No players selected")

    # Player selection mode
    if 'selecting_position' in st.session_state:
        st.subheader("Select Player")

        players = get_all_players()
        if len(players) > 0:
            # Filter out already selected players
            selected_players = [
                st.session_state.team1_player1,
                st.session_state.team1_player2,
                st.session_state.team2_player1,
                st.session_state.team2_player2
            ]
            available_players = players[~players['name'].isin([p for p in selected_players if p is not None])]

            # Create a grid of player buttons
            cols = st.columns(2)
            for i, (_, player) in enumerate(available_players.iterrows()):
                col_idx = i % 2
                with cols[col_idx]:
                    if st.button(player['name'], key=f"select_{player['name']}", use_container_width=True):
                        st.session_state[st.session_state.selecting_position] = player['name']
                        del st.session_state.selecting_position
                        st.rerun()
        else:
            st.warning("No players available. Please add players in the Player Management tab.")

        if st.button("Cancel Selection", key="cancel_selection"):
            if 'selecting_position' in st.session_state:
                del st.session_state.selecting_position
            st.rerun()

    # Check if all players are selected
    all_players_selected = (
            st.session_state.team1_player1 is not None and
            st.session_state.team1_player2 is not None and
            st.session_state.team2_player1 is not None and
            st.session_state.team2_player2 is not None
    )

    # Match controls
    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        if not st.session_state.match_setup_mode:
            if st.button("Setup Match", key="setup_match_btn", use_container_width=True):
                st.session_state.match_setup_mode = True
                st.session_state.team1_player1 = None
                st.session_state.team1_player2 = None
                st.session_state.team2_player1 = None
                st.session_state.team2_player2 = None
                st.rerun()
        else:
            if all_players_selected:
                if st.button("Confirm Teams", key="confirm_teams_btn", use_container_width=True):
                    st.session_state.match_setup_mode = False
                    st.rerun()
            else:
                if st.button("Cancel Setup", key="cancel_setup_btn", use_container_width=True):
                    st.session_state.match_setup_mode = False
                    st.session_state.team1_player1 = None
                    st.session_state.team1_player2 = None
                    st.session_state.team2_player1 = None
                    st.session_state.team2_player2 = None
                    st.rerun()

    # Only show winner buttons if all players are selected
    all_players_selected = (
        st.session_state.team1_player1 is not None and
        st.session_state.team1_player2 is not None and
        st.session_state.team2_player1 is not None and
        st.session_state.team2_player2 is not None
    )

    if all_players_selected and not st.session_state.match_setup_mode:
        with col2:
            if st.button("Team 1 Wins! 🏆", key="team1_wins_btn", use_container_width=True):
                # Record match with team 1 as winner
                record_match(
                    st.session_state.team1_player1,
                    st.session_state.team1_player2,
                    st.session_state.team2_player1,
                    st.session_state.team2_player2,
                    winner=1
                )
                # Update ratings
                update_ratings(
                    st.session_state.team1_player1,
                    st.session_state.team1_player2,
                    st.session_state.team2_player1,
                    st.session_state.team2_player2,
                    winner=1
                )
                save_data()
                st.success("Match recorded! Team 1 wins!")
                # Reset match setup
                st.session_state.team1_player1 = None
                st.session_state.team1_player2 = None
                st.session_state.team2_player1 = None
                st.session_state.team2_player2 = None
                st.rerun()

        with col3:
            if st.button("Team 2 Wins! 🏆", key="team2_wins_btn", use_container_width=True):
                # Record match with team 2 as winner
                record_match(
                    st.session_state.team1_player1,
                    st.session_state.team1_player2,
                    st.session_state.team2_player1,
                    st.session_state.team2_player2,
                    winner=2
                )
                # Update ratings
                update_ratings(
                    st.session_state.team1_player1,
                    st.session_state.team1_player2,
                    st.session_state.team2_player1,
                    st.session_state.team2_player2,
                    winner=2
                )
                save_data()
                st.success("Match recorded! Team 2 wins!")
                # Reset match setup
                st.session_state.team1_player1 = None
                st.session_state.team1_player2 = None
                st.session_state.team2_player1 = None
                st.session_state.team2_player2 = None
                st.rerun()

    # Recent matches
    st.divider()
    st.subheader("Recent Matches")
    recent_matches = get_recent_matches(limit=5)
    if len(recent_matches) > 0:
        for _, match in recent_matches.iterrows():
            st.info(f"{match['date_formatted']}: {match['result']}")
    else:
        st.info("No matches recorded yet.")

with tab2:
    st.header("Leaderboard")

    leaderboard = get_leaderboard()
    if len(leaderboard) > 0:
        # Format the leaderboard for display
        display_board = leaderboard.copy()
        display_board['Rating'] = display_board['display_rating'].round(1)
        display_board['Uncertainty'] = display_board['sigma'].round(2)

        # Add player stats
        display_board['Matches'] = display_board['name'].apply(lambda x: get_player_stats(x)['matches_played'])
        display_board['Wins'] = display_board['name'].apply(lambda x: get_player_stats(x)['wins'])
        display_board['Win Rate'] = display_board['name'].apply(lambda x: f"{get_player_stats(x)['win_rate']:.1f}%")

        # Display the leaderboard with rank
        st.dataframe(
            display_board[['name', 'rank', 'Rating', 'Uncertainty', 'Matches', 'Wins', 'Win Rate']].rename(columns={'name': 'Player', 'rank': 'Rank'}),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No players in the leaderboard yet.")

with tab3:
    st.header("Player Management")

    # Add new player
    with st.form("add_player_form"):
        st.subheader("Add New Player")
        new_player_name = st.text_input("Player Name")
        submit_button = st.form_submit_button("Add Player")

        if submit_button and new_player_name:
            if add_player(new_player_name):
                st.success(f"Player {new_player_name} added successfully!")
            else:
                st.error("Player already exists or name is empty.")

    # List all players
    st.subheader("All Players")
    players = get_all_players()
    if len(players) > 0:
        for _, player in players.iterrows():
            with st.expander(f"{player['name']}"):
                stats = get_player_stats(player['name'])

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Rating", f"{(player['mu'] - 3*player['sigma']):.1f}")
                with col2:
                    st.metric("Matches", stats['matches_played'])
                with col3:
                    st.metric("Win Rate", f"{stats['win_rate']:.1f}%")

                # Show frequent teammates
                teammates = get_most_frequent_teammates(player['name'])
                if teammates:
                    st.subheader("Frequent Teammates")
                    for teammate in teammates:
                        st.info(f"{teammate['name']} ({teammate['count']} matches)")
    else:
        st.info("No players added yet.")

# Footer
st.divider()
st.caption("Table Soccer Tracker - Built with Streamlit and OpenSkill")

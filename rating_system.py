from openskill.models import PlackettLuce
import pandas as pd
import streamlit as st

model = PlackettLuce()

# Configure OpenSkill with TrueSkill algorithm

def update_ratings(team1_player1, team1_player2, team2_player1, team2_player2, winner):
    """Update player ratings based on match result"""
    # Get current ratings
    players_df = st.session_state.players

    # Find player ratings
    t1p1_idx = players_df.index[players_df['name'] == team1_player1][0]
    t1p2_idx = players_df.index[players_df['name'] == team1_player2][0]
    t2p1_idx = players_df.index[players_df['name'] == team2_player1][0]
    t2p2_idx = players_df.index[players_df['name'] == team2_player2][0]

    # Create rating objects
    t1p1_rating = model.rating(mu=players_df.at[t1p1_idx, 'mu'], 
                                   sigma=players_df.at[t1p1_idx, 'sigma'])
    t1p2_rating = model.rating(mu=players_df.at[t1p2_idx, 'mu'], 
                                   sigma=players_df.at[t1p2_idx, 'sigma'])
    t2p1_rating = model.rating(mu=players_df.at[t2p1_idx, 'mu'], 
                                   sigma=players_df.at[t2p1_idx, 'sigma'])
    t2p2_rating = model.rating(mu=players_df.at[t2p2_idx, 'mu'], 
                                   sigma=players_df.at[t2p2_idx, 'sigma'])

    # Set up teams
    team1 = [t1p1_rating, t1p2_rating]
    team2 = [t2p1_rating, t2p2_rating]

    # Determine ranks based on winner
    ranks = [0, 1] if winner == 1 else [1, 0]

    # Update ratings
    new_ratings = model.rate([team1, team2], ranks=ranks)

    # Extract new ratings
    new_t1p1, new_t1p2 = new_ratings[0]
    new_t2p1, new_t2p2 = new_ratings[1]

    # Update dataframe
    players_df.at[t1p1_idx, 'mu'] = new_t1p1.mu
    players_df.at[t1p1_idx, 'sigma'] = new_t1p1.sigma

    players_df.at[t1p2_idx, 'mu'] = new_t1p2.mu
    players_df.at[t1p2_idx, 'sigma'] = new_t1p2.sigma

    players_df.at[t2p1_idx, 'mu'] = new_t2p1.mu
    players_df.at[t2p1_idx, 'sigma'] = new_t2p1.sigma

    players_df.at[t2p2_idx, 'mu'] = new_t2p2.mu
    players_df.at[t2p2_idx, 'sigma'] = new_t2p2.sigma

def get_display_rating(mu, sigma):
    """Calculate display rating (mu - 3*sigma)"""
    return mu - 3 * sigma

# Define thresholds for ranks
RANK_THRESHOLDS = {
    'Diamond': 40,
    'Gold': 30,
    'Silver': 20,
    'Bronze': -9999
}

def assign_rank(display_rating):
    """Assign a rank based on the display rating"""
    for rank, threshold in RANK_THRESHOLDS.items():
        if display_rating >= threshold:
            return rank
    return 'Unranked'

def get_leaderboard():
    """Return players sorted by rating with ranks if 10 or more matches are played"""
    if len(st.session_state.players) == 0:
        return pd.DataFrame()

    leaderboard = st.session_state.players.copy()
    leaderboard['display_rating'] = leaderboard.apply(
        lambda x: get_display_rating(x['mu'], x['sigma']), axis=1
    )

    if len(st.session_state.matches) >= 10:
        leaderboard['rank'] = leaderboard['display_rating'].apply(assign_rank)
    else:
        leaderboard['rank'] = 'Unranked'

    return leaderboard.sort_values('display_rating', ascending=False)
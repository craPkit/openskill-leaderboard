import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

from datetime import datetime

conn: GSheetsConnection = None


# Initialize session state for data storage
def initialize_data():
    global conn
    conn = st.connection("gsheets", type=GSheetsConnection)
    st.session_state.players = pd.DataFrame(columns=[
        'name', 'mu', 'sigma', 'created_at', 'last_played'
    ])
    st.session_state.matches = pd.DataFrame(columns=[
        'date', 'team1_player1', 'team1_player2',
        'team2_player1', 'team2_player2', 'winner'
    ])
    load_data_from_google_sheets()


# Player management functions
def add_player(name):
    """Add a new player with default rating"""
    if name:
        if st.session_state.players.empty:
            # Directly add the player if the DataFrame is empty
            new_player = pd.DataFrame({
                'name': [name],
                'mu': [25.0],  # Default OpenSkill mu value
                'sigma': [8.333],  # Default OpenSkill sigma value
                'created_at': [datetime.now()],
                'last_played': [None]
            })
            st.session_state.players = pd.concat([st.session_state.players, new_player],
                                                 ignore_index=True)
            save_data_to_google_sheets()
            return True
        elif 'name' in st.session_state.players.columns and not any(
                st.session_state.players['name'] == name):
            # Add the player if the name does not already exist
            new_player = pd.DataFrame({
                'name': [name],
                'mu': [25.0],  # Default OpenSkill mu value
                'sigma': [8.333],  # Default OpenSkill sigma value
                'created_at': [datetime.now()],
                'last_played': [None]
            })
            st.session_state.players = pd.concat([st.session_state.players, new_player],
                                                 ignore_index=True)
            save_data_to_google_sheets()
            return True
    return False


def get_all_players():
    """Return all players sorted by name"""
    if 'sorted_players' not in st.session_state:
        if len(st.session_state.players) > 0:
            st.session_state.sorted_players = st.session_state.players.sort_values('name')
        else:
            st.session_state.sorted_players = st.session_state.players
    return st.session_state.sorted_players


# Match management functions
def record_match(team1_player1, team1_player2, team2_player1, team2_player2, winner):
    """Record a match result"""
    new_match = pd.DataFrame({
        'date': [datetime.now()],
        'team1_player1': [team1_player1],
        'team1_player2': [team1_player2],
        'team2_player1': [team2_player1],
        'team2_player2': [team2_player2],
        'winner': [winner]  # 1 for team1, 2 for team2
    })

    st.session_state.matches = pd.concat([st.session_state.matches, new_match], ignore_index=True)

    # Update last_played timestamp for all players
    players_to_update = [team1_player1, team1_player2, team2_player1, team2_player2]
    for player in players_to_update:
        idx = st.session_state.players.index[st.session_state.players['name'] == player][0]
        st.session_state.players.at[idx, 'last_played'] = datetime.now()

    # Save data to Google Sheets only once
    save_data_to_google_sheets()

# Data persistence functions
def save_data_to_google_sheets():
    global conn
    players_data = st.session_state.players.copy()
    matches_data = st.session_state.matches.copy()

    if not players_data.empty:
        players_data['created_at'] = players_data['created_at'].astype(str)
        players_data['last_played'] = players_data['last_played'].astype(str)
        st.session_state.players = pd.DataFrame(players_data)
        conn.update(worksheet="Players", data=players_data)

    if not matches_data.empty:
        matches_data['date'] = matches_data['date'].astype(str)
        st.session_state.matches = pd.DataFrame(matches_data)
        conn.update(worksheet="Matches", data=matches_data)


def load_data_from_google_sheets():
    global conn
    players_sheet = conn.read(worksheet="Players")
    matches_sheet = conn.read(worksheet="Matches")

    st.session_state.players = pd.DataFrame(data=players_sheet,
                                            columns=['name', 'mu', 'sigma', 'created_at',
                                                     'last_played'])
    st.session_state.matches = pd.DataFrame(data=matches_sheet,
                                            columns=['date', 'team1_player1', 'team1_player2',
                                                     'team2_player1', 'team2_player2', 'winner'])

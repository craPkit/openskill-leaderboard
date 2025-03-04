import pandas as pd
import streamlit as st
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# Initialize session state for data storage
def initialize_data():
    if 'players' not in st.session_state:
        st.session_state.players = pd.DataFrame(columns=[
            'name', 'mu', 'sigma', 'created_at', 'last_played'
        ])
    if 'matches' not in st.session_state:
        st.session_state.matches = pd.DataFrame(columns=[
            'date', 'team1_player1', 'team1_player2',
            'team2_player1', 'team2_player2', 'winner'
        ])
    if 'data_loaded' not in st.session_state:
        load_data_from_google_sheets()
        st.session_state.data_loaded = True


def initialize_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        r'C:\Users\ivayl\Downloads\wuzzler-452700-d0b4a9f87b67.json', scope)
    client = gspread.authorize(creds)
    return client


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
            st.session_state.players = pd.concat([st.session_state.players, new_player], ignore_index=True)
            save_data()
            return True
        elif 'name' in st.session_state.players.columns and not any(st.session_state.players['name'] == name):
            # Add the player if the name does not already exist
            new_player = pd.DataFrame({
                'name': [name],
                'mu': [25.0],  # Default OpenSkill mu value
                'sigma': [8.333],  # Default OpenSkill sigma value
                'created_at': [datetime.now()],
                'last_played': [None]
            })
            st.session_state.players = pd.concat([st.session_state.players, new_player], ignore_index=True)
            save_data()
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


def save_data():
    save_data_to_google_sheets()


# Data persistence functions
def save_data_to_google_sheets():
    client = initialize_google_sheets()
    players_sheet = client.open("wuzzler").worksheet("Players")
    matches_sheet = client.open("wuzzler").worksheet("Matches")

    # Convert Timestamps to strings
    players_data = st.session_state.players.copy()
    if not players_data.empty:
        players_data['created_at'] = players_data['created_at'].astype(str)
        players_data['last_played'] = players_data['last_played'].astype(str)
        # Check if the players sheet is empty and initialize it
        if players_sheet.row_count == 1 and players_sheet.col_count == 1:
            players_sheet.update([players_data.columns.values.tolist()])
        players_sheet.update([players_data.columns.values.tolist()] + players_data.values.tolist())

    matches_data = st.session_state.matches.copy()
    # Check if the matches data is empty
    if not matches_data.empty:
        matches_data['date'] = matches_data['date'].astype(str)
        # Check if the matches sheet is empty and initialize it
        if matches_sheet.row_count == 1 and matches_sheet.col_count == 1:
            matches_sheet.update([matches_data.columns.values.tolist()])

        matches_sheet.update([matches_data.columns.values.tolist()] + matches_data.values.tolist())


def load_data_from_google_sheets():
    client = initialize_google_sheets()
    players_sheet = client.open("wuzzler").worksheet("Players")
    matches_sheet = client.open("wuzzler").worksheet("Matches")
    
    players_data = players_sheet.get_all_records(expected_headers=['name', 'mu', 'sigma', 'created_at', 'last_played'])
    matches_data = matches_sheet.get_all_records(expected_headers=['date', 'team1_player1', 'team1_player2', 'team2_player1', 'team2_player2', 'winner'])

    st.session_state.players = pd.DataFrame(players_data)
    st.session_state.matches = pd.DataFrame(matches_data)

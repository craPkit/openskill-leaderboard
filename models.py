import pandas as pd
import streamlit as st
from datetime import datetime
import os

# Initialize session state for data storage
def initialize_data():
    load_data()
    if 'players' not in st.session_state:
        st.session_state.players = pd.DataFrame(columns=[
            'name', 'mu', 'sigma', 'created_at', 'last_played'
        ])

    if 'matches' not in st.session_state:
        st.session_state.matches = pd.DataFrame(columns=[
            'date', 'team1_player1', 'team1_player2',
            'team2_player1', 'team2_player2', 'winner'
        ])

# Player management functions
def add_player(name):
    """Add a new player with default rating"""
    if name and not any(st.session_state.players['name'] == name):
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
    if len(st.session_state.players) > 0:
        return st.session_state.players.sort_values('name')
    return st.session_state.players

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
    for player in [team1_player1, team1_player2, team2_player1, team2_player2]:
        idx = st.session_state.players.index[st.session_state.players['name'] == player][0]
        st.session_state.players.at[idx, 'last_played'] = datetime.now()

    save_data()
    return True

# Data persistence functions
def save_data():
    """Save data to a JSON file"""
    players_json = st.session_state.players.to_json()
    matches_json = st.session_state.matches.to_json()

    with open('players.json', 'w') as f:
        f.write(players_json)

    with open('matches.json', 'w') as f:
        f.write(matches_json)

def load_data():
    """Load data from a JSON file"""
    if os.path.exists('players.json'):
        with open('players.json', 'r') as f:
            players_json = f.read()
        st.session_state.players = pd.read_json(players_json)

    if os.path.exists('matches.json'):
        with open('matches.json', 'r') as f:
            matches_json = f.read()
        st.session_state.matches = pd.read_json(matches_json)

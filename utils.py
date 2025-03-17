import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

def get_player_stats(player_name):
    """Get statistics for a specific player"""
    if len(st.session_state.matches) == 0:
        return {
            'matches_played': 0,
            'wins': 0,
            'losses': 0,
            'win_rate': 0.0
        }

    matches = st.session_state.matches

    # Count matches where player participated
    player_matches = matches[
        (matches['team1_player1'] == player_name) | 
        (matches['team1_player2'] == player_name) | 
        (matches['team2_player1'] == player_name) | 
        (matches['team2_player2'] == player_name)
    ]

    matches_played = len(player_matches)

    if matches_played == 0:
        return {
            'matches_played': 0,
            'wins': 0,
            'losses': 0,
            'win_rate': 0.0
        }

    # Count wins
    team1_wins = len(player_matches[
        ((player_matches['team1_player1'] == player_name) | 
         (player_matches['team1_player2'] == player_name)) &
        (player_matches['winner'] == 1)
    ])

    team2_wins = len(player_matches[
        ((player_matches['team2_player1'] == player_name) | 
         (player_matches['team2_player2'] == player_name)) &
        (player_matches['winner'] == 2)
    ])

    wins = team1_wins + team2_wins
    losses = matches_played - wins
    win_rate = (wins / matches_played) * 100

    return {
        'matches_played': matches_played,
        'wins': wins,
        'losses': losses,
        'win_rate': win_rate
    }

def get_recent_matches(limit=10):
    """Get recent matches with results"""
    if len(st.session_state.matches) == 0:
        return pd.DataFrame()

    matches = st.session_state.matches.copy().sort_values('date', ascending=False).head(limit)

    # Format for display
    matches['result'] = matches.apply(
        lambda x: f"{x['team1_player1']} & {x['team1_player2']} vs {x['team2_player1']} & {x['team2_player2']} - " + 
                 (f"Team 1 Won" if x['winner'] == 1 else f"Team 2 Won"),
        axis=1
    )

    matches['date_formatted'] = matches['date'].dt.strftime('%Y-%m-%d %H:%M')

    return matches[['date_formatted', 'result']]

def get_most_frequent_teammates(player_name, limit=3):
    """Find most frequent teammates for a player"""
    if len(st.session_state.matches) == 0:
        return []

    matches = st.session_state.matches

    # Find teammates from team1
    team1_mates = matches[matches['team1_player1'] == player_name]['team1_player2'].tolist() + \
                 matches[matches['team1_player2'] == player_name]['team1_player1'].tolist()

    # Find teammates from team2
    team2_mates = matches[matches['team2_player1'] == player_name]['team2_player2'].tolist() + \
                 matches[matches['team2_player2'] == player_name]['team2_player1'].tolist()

    # Combine and count
    all_teammates = team1_mates + team2_mates

    if not all_teammates:
        return []

    teammate_counts = pd.Series(all_teammates).value_counts().head(limit)

    return [{"name": name, "count": count} for name, count in teammate_counts.items()]

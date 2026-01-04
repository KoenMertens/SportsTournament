import streamlit as st
import sqlite3
from datetime import datetime
from typing import List, Tuple
import pandas as pd

# Page config
st.set_page_config(
    page_title="Tafeltennis Clubkampioenschap",
    page_icon="🏓",
    layout="wide"
)

# Database setup
DB_NAME = "tournament.db"

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Tournaments table
    c.execute('''
        CREATE TABLE IF NOT EXISTS tournaments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sport_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Players table
    c.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            tournament_id INTEGER,
            FOREIGN KEY (tournament_id) REFERENCES tournaments(id)
        )
    ''')
    
    # Matches table
    c.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tournament_id INTEGER,
            player1_id INTEGER,
            player2_id INTEGER,
            player1_score INTEGER,
            player2_score INTEGER,
            played_at TIMESTAMP,
            FOREIGN KEY (tournament_id) REFERENCES tournaments(id),
            FOREIGN KEY (player1_id) REFERENCES players(id),
            FOREIGN KEY (player2_id) REFERENCES players(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_tournaments() -> List[Tuple]:
    """Get all tournaments"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id, name, sport_type, created_at FROM tournaments ORDER BY created_at DESC')
    tournaments = c.fetchall()
    conn.close()
    return tournaments

def create_tournament(name: str, sport_type: str) -> int:
    """Create a new tournament and return its ID"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO tournaments (name, sport_type) VALUES (?, ?)', (name, sport_type))
    tournament_id = c.lastrowid
    conn.commit()
    conn.close()
    return tournament_id

def get_players(tournament_id: int) -> List[Tuple]:
    """Get all players for a tournament"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id, name FROM players WHERE tournament_id = ?', (tournament_id,))
    players = c.fetchall()
    conn.close()
    return players

def add_player(tournament_id: int, name: str):
    """Add a player to a tournament"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO players (tournament_id, name) VALUES (?, ?)', (tournament_id, name))
    conn.commit()
    conn.close()

def get_matches(tournament_id: int) -> List[Tuple]:
    """Get all matches for a tournament"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT m.id, p1.name, p2.name, m.player1_score, m.player2_score, m.played_at
        FROM matches m
        JOIN players p1 ON m.player1_id = p1.id
        JOIN players p2 ON m.player2_id = p2.id
        WHERE m.tournament_id = ?
        ORDER BY m.played_at DESC
    ''', (tournament_id,))
    matches = c.fetchall()
    conn.close()
    return matches

def save_match(tournament_id: int, player1_id: int, player2_id: int, score1: int, score2: int):
    """Save a match result"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO matches (tournament_id, player1_id, player2_id, player1_score, player2_score, played_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (tournament_id, player1_id, player2_id, score1, score2, datetime.now()))
    conn.commit()
    conn.close()

def generate_round_robin_matches(tournament_id: int):
    """Generate all matches for a round-robin tournament (everyone vs everyone)"""
    players = get_players(tournament_id)
    if len(players) < 2:
        return []
    
    matches = []
    for i in range(len(players)):
        for j in range(i + 1, len(players)):
            matches.append((players[i][0], players[j][0]))
    return matches

def get_standings(tournament_id: int) -> pd.DataFrame:
    """Calculate tournament standings"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Get all players
    c.execute('SELECT id, name FROM players WHERE tournament_id = ?', (tournament_id,))
    players = c.fetchall()
    
    # Initialize stats for each player
    stats = {player[0]: {'name': player[1], 'wins': 0, 'losses': 0, 'points_for': 0, 'points_against': 0} 
             for player in players}
    
    # Get matches with player IDs
    c.execute('''
        SELECT player1_id, player2_id, player1_score, player2_score
        FROM matches
        WHERE tournament_id = ?
    ''', (tournament_id,))
    matches = c.fetchall()
    conn.close()
    
    # Calculate stats from matches
    for match in matches:
        p1_id, p2_id, score1, score2 = match
        
        if p1_id in stats:
            stats[p1_id]['points_for'] += score1
            stats[p1_id]['points_against'] += score2
            if score1 > score2:
                stats[p1_id]['wins'] += 1
            else:
                stats[p1_id]['losses'] += 1
        
        if p2_id in stats:
            stats[p2_id]['points_for'] += score2
            stats[p2_id]['points_against'] += score1
            if score2 > score1:
                stats[p2_id]['wins'] += 1
            else:
                stats[p2_id]['losses'] += 1
    
    # Convert to DataFrame
    standings_data = []
    for player_id, stat in stats.items():
        standings_data.append({
            'Speler': stat['name'],
            'Gewonnen': stat['wins'],
            'Verloren': stat['losses'],
            'Punten Voor': stat['points_for'],
            'Punten Tegen': stat['points_against'],
            'Saldo': stat['points_for'] - stat['points_against']
        })
    
    df = pd.DataFrame(standings_data)
    if not df.empty:
        df = df.sort_values(['Gewonnen', 'Saldo'], ascending=[False, False])
        df.reset_index(drop=True, inplace=True)
        df.index = df.index + 1
    
    return df

# Initialize database
init_db()

# Main app
st.title("🏓 Tafeltennis Clubkampioenschap")
st.markdown("Toernooi beheer - Iedereen tegen iedereen")

# Sidebar for navigation
page = st.sidebar.selectbox("Menu", ["Toernooien", "Nieuw Toernooi"])

if page == "Toernooien":
    tournaments = get_tournaments()
    
    if not tournaments:
        st.info("Nog geen toernooien. Maak er een aan via 'Nieuw Toernooi'.")
    else:
        st.subheader("Beschikbare Toernooien")
        
        for tournament in tournaments:
            tournament_id, name, sport_type, created_at = tournament
            
            with st.expander(f"🏆 {name} ({sport_type})"):
                # Tournament info
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Sport:** {sport_type}")
                    st.write(f"**Aangemaakt:** {created_at}")
                    
                    # Add player section
                    st.subheader("Speler Toevoegen")
                    new_player = st.text_input(f"Nieuwe speler voor {name}", key=f"player_{tournament_id}")
                    if st.button(f"Toevoegen", key=f"add_player_{tournament_id}"):
                        if new_player:
                            add_player(tournament_id, new_player)
                            st.success(f"{new_player} toegevoegd!")
                            st.rerun()
                
                with col2:
                    # Players list
                    players = get_players(tournament_id)
                    if players:
                        st.subheader("Spelers")
                        for player in players:
                            st.write(f"- {player[1]}")
                    else:
                        st.info("Nog geen spelers toegevoegd")
                
                # Standings
                if players and len(players) >= 2:
                    st.subheader("Stand")
                    standings = get_standings(tournament_id)
                    if not standings.empty:
                        st.dataframe(standings, use_container_width=True)
                    
                    # Matches section
                    st.subheader("Wedstrijd Invoeren")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    player_names = [p[1] for p in players]
                    player_dict = {p[1]: p[0] for p in players}
                    
                    with col1:
                        player1 = st.selectbox("Speler 1", player_names, key=f"p1_{tournament_id}")
                    with col2:
                        score1 = st.number_input("Score 1", min_value=0, key=f"s1_{tournament_id}")
                    with col3:
                        player2 = st.selectbox("Speler 2", player_names, key=f"p2_{tournament_id}")
                    with col4:
                        score2 = st.number_input("Score 2", min_value=0, key=f"s2_{tournament_id}")
                    
                    if player1 == player2:
                        st.warning("Kies verschillende spelers!")
                    elif st.button("Wedstrijd Opslaan", key=f"save_match_{tournament_id}"):
                        save_match(tournament_id, player_dict[player1], player_dict[player2], score1, score2)
                        st.success("Wedstrijd opgeslagen!")
                        st.rerun()
                    
                    # Match history
                    matches = get_matches(tournament_id)
                    if matches:
                        st.subheader("Wedstrijdgeschiedenis")
                        match_data = []
                        for match in matches:
                            match_data.append({
                                'Speler 1': match[1],
                                'Score 1': match[3],
                                'Score 2': match[4],
                                'Speler 2': match[2],
                                'Datum': match[5]
                            })
                        match_df = pd.DataFrame(match_data)
                        st.dataframe(match_df, use_container_width=True)
                else:
                    st.info("Voeg minimaal 2 spelers toe om wedstrijden te kunnen spelen")

elif page == "Nieuw Toernooi":
    st.subheader("Nieuw Toernooi Aanmaken")
    
    tournament_name = st.text_input("Toernooi Naam")
    sport_type = st.selectbox("Sport Type", ["Tafeltennis", "Padel"])
    
    if st.button("Toernooi Aanmaken"):
        if tournament_name:
            tournament_id = create_tournament(tournament_name, sport_type)
            st.success(f"Toernooi '{tournament_name}' aangemaakt!")
            st.info("Ga naar 'Toernooien' om spelers toe te voegen en wedstrijden in te voeren.")
        else:
            st.error("Voer een toernooi naam in")


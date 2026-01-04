"""
Database setup and connection management
"""
import sqlite3
from typing import Optional

DB_NAME = "tournament.db"


def get_connection() -> sqlite3.Connection:
    """Get database connection"""
    return sqlite3.connect(DB_NAME)


def init_db():
    """Initialize the database with all required tables"""
    conn = get_connection()
    c = conn.cursor()
    
    # Migrate existing tournaments table if needed (for backward compatibility)
    try:
        c.execute("SELECT team_type, has_consolation FROM tournaments LIMIT 1")
    except sqlite3.OperationalError:
        # Columns don't exist, add them
        try:
            c.execute('ALTER TABLE tournaments ADD COLUMN team_type TEXT DEFAULT "single"')
        except sqlite3.OperationalError:
            pass  # Column might already exist
        try:
            c.execute('ALTER TABLE tournaments ADD COLUMN has_consolation INTEGER DEFAULT 0')
        except sqlite3.OperationalError:
            pass  # Column might already exist
        conn.commit()
    
    # Players table - global, reusable across tournaments
    c.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    
    # Tournaments table
    c.execute('''
        CREATE TABLE IF NOT EXISTS tournaments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sport_type TEXT NOT NULL,
            tournament_type TEXT NOT NULL,
            team_type TEXT NOT NULL,
            has_consolation INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Teams table - teams belong to a tournament, can have 1 or 2 players
    c.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tournament_id INTEGER NOT NULL,
            player1_id INTEGER NOT NULL,
            player2_id INTEGER,
            FOREIGN KEY (tournament_id) REFERENCES tournaments(id) ON DELETE CASCADE,
            FOREIGN KEY (player1_id) REFERENCES players(id),
            FOREIGN KEY (player2_id) REFERENCES players(id)
        )
    ''')
    
    # Poules table - poules within tournaments
    c.execute('''
        CREATE TABLE IF NOT EXISTS poules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tournament_id INTEGER NOT NULL,
            phase TEXT NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (tournament_id) REFERENCES tournaments(id) ON DELETE CASCADE,
            UNIQUE(tournament_id, phase, name)
        )
    ''')
    
    # Matches table - matches between teams
    c.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tournament_id INTEGER NOT NULL,
            phase TEXT NOT NULL,
            poule_id INTEGER,
            team1_id INTEGER NOT NULL,
            team2_id INTEGER NOT NULL,
            team1_score INTEGER,
            team2_score INTEGER,
            played_at TIMESTAMP,
            FOREIGN KEY (tournament_id) REFERENCES tournaments(id) ON DELETE CASCADE,
            FOREIGN KEY (poule_id) REFERENCES poules(id),
            FOREIGN KEY (team1_id) REFERENCES teams(id),
            FOREIGN KEY (team2_id) REFERENCES teams(id)
        )
    ''')
    
    conn.commit()
    conn.close()


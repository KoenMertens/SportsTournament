"""
Player model - players are unique per tournament
"""
import sqlite3
from typing import Optional, List
from database import get_connection


class Player:
    """Represents a player (unique per tournament)"""
    
    def __init__(self, id: Optional[int] = None, tournament_id: Optional[int] = None, name: str = ""):
        self.id = id
        self.tournament_id = tournament_id
        self.name = name
    
    def save(self) -> int:
        """Save player to database, returns player ID"""
        if not self.tournament_id:
            raise ValueError("Tournament ID is required")
        
        conn = get_connection()
        c = conn.cursor()
        
        if self.id:
            # Update existing
            c.execute('UPDATE players SET name = ?, tournament_id = ? WHERE id = ?', 
                     (self.name, self.tournament_id, self.id))
            conn.commit()
            conn.close()
            return self.id
        else:
            # Insert new
            c.execute('INSERT INTO players (tournament_id, name) VALUES (?, ?)', 
                     (self.tournament_id, self.name))
            player_id = c.lastrowid
            conn.commit()
            conn.close()
            self.id = player_id
            return player_id
    
    @staticmethod
    def get_by_id(player_id: int) -> Optional['Player']:
        """Get player by ID"""
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT id, tournament_id, name FROM players WHERE id = ?', (player_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            return Player(id=row[0], tournament_id=row[1], name=row[2])
        return None
    
    @staticmethod
    def get_by_tournament(tournament_id: int) -> List['Player']:
        """Get all players for a tournament"""
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT id, tournament_id, name FROM players WHERE tournament_id = ? ORDER BY name', 
                 (tournament_id,))
        rows = c.fetchall()
        conn.close()
        
        return [Player(id=row[0], tournament_id=row[1], name=row[2]) for row in rows]
    
    @staticmethod
    def find_by_name_in_tournament(tournament_id: int, name: str) -> Optional['Player']:
        """Find player by name in a specific tournament (case-insensitive)"""
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT id, tournament_id, name FROM players WHERE tournament_id = ? AND LOWER(name) = LOWER(?)', 
                 (tournament_id, name))
        row = c.fetchone()
        conn.close()
        
        if row:
            return Player(id=row[0], tournament_id=row[1], name=row[2])
        return None
    
    @staticmethod
    def create_or_get_in_tournament(tournament_id: int, name: str) -> 'Player':
        """Create player in tournament if not exists, otherwise get existing"""
        existing = Player.find_by_name_in_tournament(tournament_id, name)
        if existing:
            return existing
        
        player = Player(tournament_id=tournament_id, name=name)
        player.save()
        return player
    
    def __repr__(self):
        return f"Player(id={self.id}, tournament_id={self.tournament_id}, name='{self.name}')"


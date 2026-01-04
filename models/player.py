"""
Player model - global players, reusable across tournaments
"""
import sqlite3
from typing import Optional, List
from database import get_connection


class Player:
    """Represents a player (global, can participate in multiple tournaments)"""
    
    def __init__(self, id: Optional[int] = None, name: str = ""):
        self.id = id
        self.name = name
    
    def save(self) -> int:
        """Save player to database, returns player ID"""
        conn = get_connection()
        c = conn.cursor()
        
        if self.id:
            # Update existing
            c.execute('UPDATE players SET name = ? WHERE id = ?', (self.name, self.id))
            conn.commit()
            conn.close()
            return self.id
        else:
            # Insert new
            c.execute('INSERT INTO players (name) VALUES (?)', (self.name,))
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
        c.execute('SELECT id, name FROM players WHERE id = ?', (player_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            return Player(id=row[0], name=row[1])
        return None
    
    @staticmethod
    def get_all() -> List['Player']:
        """Get all players"""
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT id, name FROM players ORDER BY name')
        rows = c.fetchall()
        conn.close()
        
        return [Player(id=row[0], name=row[1]) for row in rows]
    
    @staticmethod
    def find_by_name(name: str) -> Optional['Player']:
        """Find player by name (case-insensitive)"""
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT id, name FROM players WHERE LOWER(name) = LOWER(?)', (name,))
        row = c.fetchone()
        conn.close()
        
        if row:
            return Player(id=row[0], name=row[1])
        return None
    
    @staticmethod
    def create_or_get(name: str) -> 'Player':
        """Create player if not exists, otherwise get existing"""
        existing = Player.find_by_name(name)
        if existing:
            return existing
        
        player = Player(name=name)
        player.save()
        return player
    
    def __repr__(self):
        return f"Player(id={self.id}, name='{self.name}')"


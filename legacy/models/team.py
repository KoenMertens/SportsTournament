"""
Team model - teams belong to tournaments, can have 1 or 2 players
"""
import sqlite3
from typing import Optional, List
from database import get_connection
from .player import Player


class Team:
    """Represents a team in a tournament (1 or 2 players)"""
    
    def __init__(self, id: Optional[int] = None, tournament_id: Optional[int] = None, 
                 player1: Optional[Player] = None, player2: Optional[Player] = None):
        self.id = id
        self.tournament_id = tournament_id
        self.player1 = player1
        self.player2 = player2
    
    @property
    def is_single(self) -> bool:
        """Check if team has only 1 player (individual tournament)"""
        return self.player2 is None
    
    @property
    def is_double(self) -> bool:
        """Check if team has 2 players (padel tournament)"""
        return self.player2 is not None
    
    @property
    def display_name(self) -> str:
        """Get display name for the team"""
        if self.is_single:
            return self.player1.name if self.player1 else ""
        else:
            names = [p.name for p in [self.player1, self.player2] if p]
            return " / ".join(names)
    
    def save(self) -> int:
        """Save team to database, returns team ID"""
        if not self.tournament_id:
            raise ValueError("Tournament ID is required")
        if not self.player1:
            raise ValueError("Player 1 is required")
        if self.player1.id is None:
            raise ValueError("Player 1 must be saved first")
        if self.player2 and self.player2.id is None:
            raise ValueError("Player 2 must be saved first")
        
        conn = get_connection()
        c = conn.cursor()
        
        player2_id = self.player2.id if self.player2 else None
        
        if self.id:
            # Update existing
            c.execute('''
                UPDATE teams 
                SET tournament_id = ?, player1_id = ?, player2_id = ?
                WHERE id = ?
            ''', (self.tournament_id, self.player1.id, player2_id, self.id))
            conn.commit()
            conn.close()
            return self.id
        else:
            # Insert new
            c.execute('''
                INSERT INTO teams (tournament_id, player1_id, player2_id)
                VALUES (?, ?, ?)
            ''', (self.tournament_id, self.player1.id, player2_id))
            team_id = c.lastrowid
            conn.commit()
            conn.close()
            self.id = team_id
            return team_id
    
    @staticmethod
    def get_by_id(team_id: int) -> Optional['Team']:
        """Get team by ID"""
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            SELECT id, tournament_id, player1_id, player2_id
            FROM teams
            WHERE id = ?
        ''', (team_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            player1 = Player.get_by_id(row[2]) if row[2] else None
            player2 = Player.get_by_id(row[3]) if row[3] else None
            return Team(id=row[0], tournament_id=row[1], player1=player1, player2=player2)
        return None
    
    @staticmethod
    def get_by_tournament(tournament_id: int) -> List['Team']:
        """Get all teams for a tournament"""
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            SELECT id, tournament_id, player1_id, player2_id
            FROM teams
            WHERE tournament_id = ?
            ORDER BY id
        ''', (tournament_id,))
        rows = c.fetchall()
        conn.close()
        
        teams = []
        for row in rows:
            player1 = Player.get_by_id(row[2]) if row[2] else None
            player2 = Player.get_by_id(row[3]) if row[3] else None
            teams.append(Team(id=row[0], tournament_id=row[1], player1=player1, player2=player2))
        
        return teams
    
    def __repr__(self):
        return f"Team(id={self.id}, tournament_id={self.tournament_id}, players={self.display_name})"


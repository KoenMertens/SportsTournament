"""
Match model - matches between teams
"""
import sqlite3
from datetime import datetime
from typing import Optional, List
from enum import Enum
from database import get_connection
from .team import Team


class MatchPhase(Enum):
    """Match phases"""
    POULE = "poule"
    KNOCKOUT = "knockout"
    CONSOLATION = "consolation"


class Match:
    """Represents a match between two teams"""
    
    def __init__(self, id: Optional[int] = None, tournament_id: Optional[int] = None,
                 phase: MatchPhase = MatchPhase.POULE, poule_id: Optional[int] = None,
                 team1: Optional[Team] = None, team2: Optional[Team] = None,
                 team1_score: Optional[int] = None, team2_score: Optional[int] = None,
                 played_at: Optional[datetime] = None):
        self.id = id
        self.tournament_id = tournament_id
        self.phase = phase if isinstance(phase, MatchPhase) else MatchPhase(phase)
        self.poule_id = poule_id
        self.team1 = team1
        self.team2 = team2
        self.team1_score = team1_score
        self.team2_score = team2_score
        self.played_at = played_at
    
    @property
    def is_played(self) -> bool:
        """Check if match has been played"""
        return self.team1_score is not None and self.team2_score is not None
    
    @property
    def winner(self) -> Optional[Team]:
        """Get winning team (None if not played or tie)"""
        if not self.is_played:
            return None
        if self.team1_score > self.team2_score:
            return self.team1
        elif self.team2_score > self.team1_score:
            return self.team2
        return None  # Tie
    
    @property
    def loser(self) -> Optional[Team]:
        """Get losing team (None if not played or tie)"""
        if not self.is_played:
            return None
        if self.team1_score < self.team2_score:
            return self.team1
        elif self.team2_score < self.team1_score:
            return self.team2
        return None  # Tie
    
    def save(self) -> int:
        """Save match to database, returns match ID"""
        if not self.tournament_id:
            raise ValueError("Tournament ID is required")
        if not self.team1 or not self.team1.id:
            raise ValueError("Team 1 is required")
        if not self.team2 or not self.team2.id:
            raise ValueError("Team 2 is required")
        
        conn = get_connection()
        c = conn.cursor()
        
        phase_str = self.phase.value
        played_at = self.played_at or (datetime.now() if self.is_played else None)
        
        if self.id:
            # Update existing
            c.execute('''
                UPDATE matches
                SET tournament_id = ?, phase = ?, poule_id = ?, 
                    team1_id = ?, team2_id = ?, team1_score = ?, team2_score = ?, played_at = ?
                WHERE id = ?
            ''', (self.tournament_id, phase_str, self.poule_id, self.team1.id, self.team2.id,
                  self.team1_score, self.team2_score, played_at, self.id))
            conn.commit()
            conn.close()
            return self.id
        else:
            # Insert new
            c.execute('''
                INSERT INTO matches 
                (tournament_id, phase, poule_id, team1_id, team2_id, team1_score, team2_score, played_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (self.tournament_id, phase_str, self.poule_id, self.team1.id, self.team2.id,
                  self.team1_score, self.team2_score, played_at))
            match_id = c.lastrowid
            conn.commit()
            conn.close()
            self.id = match_id
            return match_id
    
    @staticmethod
    def get_by_id(match_id: int) -> Optional['Match']:
        """Get match by ID"""
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            SELECT id, tournament_id, phase, poule_id, team1_id, team2_id, 
                   team1_score, team2_score, played_at
            FROM matches
            WHERE id = ?
        ''', (match_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            team1 = Team.get_by_id(row[4]) if row[4] else None
            team2 = Team.get_by_id(row[5]) if row[5] else None
            played_at = datetime.fromisoformat(row[8]) if row[8] else None
            
            return Match(
                id=row[0], tournament_id=row[1], phase=MatchPhase(row[2]), poule_id=row[3],
                team1=team1, team2=team2, team1_score=row[6], team2_score=row[7], played_at=played_at
            )
        return None
    
    @staticmethod
    def get_by_tournament(tournament_id: int, phase: Optional[MatchPhase] = None) -> List['Match']:
        """Get all matches for a tournament, optionally filtered by phase"""
        conn = get_connection()
        c = conn.cursor()
        
        if phase:
            c.execute('''
                SELECT id, tournament_id, phase, poule_id, team1_id, team2_id, 
                       team1_score, team2_score, played_at
                FROM matches
                WHERE tournament_id = ? AND phase = ?
                ORDER BY played_at DESC, id
            ''', (tournament_id, phase.value))
        else:
            c.execute('''
                SELECT id, tournament_id, phase, poule_id, team1_id, team2_id, 
                       team1_score, team2_score, played_at
                FROM matches
                WHERE tournament_id = ?
                ORDER BY played_at DESC, id
            ''', (tournament_id,))
        
        rows = c.fetchall()
        conn.close()
        
        matches = []
        for row in rows:
            team1 = Team.get_by_id(row[4]) if row[4] else None
            team2 = Team.get_by_id(row[5]) if row[5] else None
            played_at = datetime.fromisoformat(row[8]) if row[8] else None
            
            matches.append(Match(
                id=row[0], tournament_id=row[1], phase=MatchPhase(row[2]), poule_id=row[3],
                team1=team1, team2=team2, team1_score=row[6], team2_score=row[7], played_at=played_at
            ))
        
        return matches
    
    def __repr__(self):
        status = f"{self.team1_score}-{self.team2_score}" if self.is_played else "Not played"
        return f"Match(id={self.id}, {self.team1.display_name if self.team1 else '?'} vs {self.team2.display_name if self.team2 else '?'}, {status})"


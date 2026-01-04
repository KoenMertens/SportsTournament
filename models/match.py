"""
Match model - matches between teams
"""
from __future__ import annotations

import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Tuple
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
                 sets: Optional[List[Tuple[int, int]]] = None,
                 played_at: Optional[datetime] = None):
        self.id = id
        self.tournament_id = tournament_id
        self.phase = phase if isinstance(phase, MatchPhase) else MatchPhase(phase)
        self.poule_id = poule_id
        self.team1 = team1
        self.team2 = team2
        self.team1_score = team1_score  # Number of sets won by team1
        self.team2_score = team2_score  # Number of sets won by team2
        self.sets = sets or []  # List of tuples: [(score1, score2), ...] for each set
        self.played_at = played_at
    
    def _calculate_set_wins(self):
        """Calculate number of sets won by each team from sets list"""
        if not self.sets:
            return 0, 0
        
        wins1, wins2 = 0, 0
        for score1, score2 in self.sets:
            if score1 > score2:
                wins1 += 1
            elif score2 > score1:
                wins2 += 1
        return wins1, wins2
    
    @property
    def is_played(self) -> bool:
        """Check if match has been played"""
        if self.sets:
            return len(self.sets) > 0
        return self.team1_score is not None and self.team2_score is not None
    
    @property
    def winner(self) -> Optional[Team]:
        """Get winning team (None if not played or tie)"""
        if not self.is_played:
            return None
        
        # Calculate wins from sets if available
        if self.sets:
            wins1, wins2 = self._calculate_set_wins()
            if wins1 > wins2:
                return self.team1
            elif wins2 > wins1:
                return self.team2
            return None  # Tie
        
        # Fallback to old method
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
        
        winner = self.winner
        if winner == self.team1:
            return self.team2
        elif winner == self.team2:
            return self.team1
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
        
        # Calculate set wins from sets if available
        if self.sets:
            wins1, wins2 = self._calculate_set_wins()
            self.team1_score = wins1
            self.team2_score = wins2
        
        # Serialize sets to JSON
        sets_json = json.dumps(self.sets) if self.sets else None
        
        if self.id:
            # Update existing
            c.execute('''
                UPDATE matches
                SET tournament_id = ?, phase = ?, poule_id = ?, 
                    team1_id = ?, team2_id = ?, team1_score = ?, team2_score = ?, sets_json = ?, played_at = ?
                WHERE id = ?
            ''', (self.tournament_id, phase_str, self.poule_id, self.team1.id, self.team2.id,
                  self.team1_score, self.team2_score, sets_json, played_at, self.id))
            conn.commit()
            conn.close()
            return self.id
        else:
            # Insert new
            c.execute('''
                INSERT INTO matches 
                (tournament_id, phase, poule_id, team1_id, team2_id, team1_score, team2_score, sets_json, played_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (self.tournament_id, phase_str, self.poule_id, self.team1.id, self.team2.id,
                  self.team1_score, self.team2_score, sets_json, played_at))
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
                   team1_score, team2_score, sets_json, played_at
            FROM matches
            WHERE id = ?
        ''', (match_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            team1 = Team.get_by_id(row[4]) if row[4] else None
            team2 = Team.get_by_id(row[5]) if row[5] else None
            sets_data = json.loads(row[8]) if row[8] else []
            sets = [tuple(s) for s in sets_data] if sets_data else []
            played_at = datetime.fromisoformat(row[9]) if row[9] else None
            
            return Match(
                id=row[0], tournament_id=row[1], phase=MatchPhase(row[2]), poule_id=row[3],
                team1=team1, team2=team2, team1_score=row[6], team2_score=row[7], 
                sets=sets, played_at=played_at
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
                       team1_score, team2_score, sets_json, played_at
                FROM matches
                WHERE tournament_id = ? AND phase = ?
                ORDER BY played_at DESC, id
            ''', (tournament_id, phase.value))
        else:
            c.execute('''
                SELECT id, tournament_id, phase, poule_id, team1_id, team2_id, 
                       team1_score, team2_score, sets_json, played_at
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
            sets_data = json.loads(row[8]) if row[8] else []
            sets = [tuple(s) for s in sets_data] if sets_data else []
            played_at = datetime.fromisoformat(row[9]) if row[9] else None
            
            matches.append(Match(
                id=row[0], tournament_id=row[1], phase=MatchPhase(row[2]), poule_id=row[3],
                team1=team1, team2=team2, team1_score=row[6], team2_score=row[7], 
                sets=sets, played_at=played_at
            ))
        
        return matches
    
    def __repr__(self):
        status = f"{self.team1_score}-{self.team2_score}" if self.is_played else "Not played"
        return f"Match(id={self.id}, {self.team1.display_name if self.team1 else '?'} vs {self.team2.display_name if self.team2 else '?'}, {status})"


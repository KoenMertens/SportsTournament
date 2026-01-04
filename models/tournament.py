"""
Tournament base class - abstract base for different tournament types
"""
import sqlite3
from abc import ABC, abstractmethod
from typing import Optional, List
from database import get_connection
from .team import Team


class Tournament(ABC):
    """Base class for all tournament types"""
    
    def __init__(self, id: Optional[int] = None, name: str = "", 
                 sport_type: str = "", tournament_type: str = "",
                 team_type: str = "single", has_consolation: bool = False,
                 created_at: Optional[str] = None):
        self.id = id
        self.name = name
        self.sport_type = sport_type
        self.tournament_type = tournament_type
        self.team_type = team_type  # "single" or "double"
        self.has_consolation = has_consolation
        self.created_at = created_at
    
    def save(self) -> int:
        """Save tournament to database, returns tournament ID"""
        conn = get_connection()
        c = conn.cursor()
        
        if self.id:
            # Update existing
            c.execute('''
                UPDATE tournaments 
                SET name = ?, sport_type = ?, tournament_type = ?, team_type = ?, has_consolation = ?
                WHERE id = ?
            ''', (self.name, self.sport_type, self.tournament_type, self.team_type, 
                  1 if self.has_consolation else 0, self.id))
            conn.commit()
            conn.close()
            return self.id
        else:
            # Insert new
            c.execute('''
                INSERT INTO tournaments (name, sport_type, tournament_type, team_type, has_consolation)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.name, self.sport_type, self.tournament_type, self.team_type, 
                  1 if self.has_consolation else 0))
            tournament_id = c.lastrowid
            conn.commit()
            conn.close()
            self.id = tournament_id
            return tournament_id
    
    @staticmethod
    def get_by_id(tournament_id: int) -> Optional['Tournament']:
        """Get tournament by ID - returns appropriate subclass instance"""
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            SELECT id, name, sport_type, tournament_type, team_type, has_consolation, created_at
            FROM tournaments
            WHERE id = ?
        ''', (tournament_id,))
        row = c.fetchone()
        conn.close()
        
        if not row:
            return None
        
        # Import here to avoid circular imports
        from tournament_types.round_robin import RoundRobinTournament
        from tournament_types.default_tournament import DefaultTournament
        
        tournament_type = row[3]
        has_consolation = bool(row[5])
        
        if tournament_type == "round_robin":
            return RoundRobinTournament(id=row[0], name=row[1], sport_type=row[2], 
                                      tournament_type=row[3], team_type=row[4],
                                      has_consolation=has_consolation, created_at=row[6])
        elif tournament_type == "default_tournament":
            return DefaultTournament(id=row[0], name=row[1], sport_type=row[2], 
                                   tournament_type=row[3], team_type=row[4],
                                   has_consolation=has_consolation, created_at=row[6])
        else:
            # Fallback to base Tournament if type not recognized
            return Tournament(id=row[0], name=row[1], sport_type=row[2], 
                            tournament_type=row[3], team_type=row[4],
                            has_consolation=has_consolation, created_at=row[6])
    
    @staticmethod
    def get_all() -> List['Tournament']:
        """Get all tournaments"""
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            SELECT id, name, sport_type, tournament_type, team_type, has_consolation, created_at
            FROM tournaments
            ORDER BY created_at DESC
        ''')
        rows = c.fetchall()
        conn.close()
        
        tournaments = []
        for row in rows:
            tournament = Tournament.get_by_id(row[0])
            if tournament:
                tournaments.append(tournament)
        return tournaments
    
    def get_teams(self) -> List[Team]:
        """Get all teams in this tournament"""
        if not self.id:
            return []
        return Team.get_by_tournament(self.id)
    
    def add_team(self, team: Team) -> int:
        """Add a team to this tournament"""
        if not self.id:
            raise ValueError("Tournament must be saved before adding teams")
        team.tournament_id = self.id
        return team.save()
    
    def get_matches(self, phase: Optional[str] = None) -> List[Match]:
        """Get all matches for this tournament, optionally filtered by phase"""
        if not self.id:
            return []
        
        from .match import MatchPhase
        phase_enum = None
        if phase:
            phase_enum = MatchPhase(phase)
        
        return Match.get_by_tournament(self.id, phase_enum)
    
    @abstractmethod
    def generate_matches(self, teams_per_poule: int = 4) -> List[Match]:
        """
        Generate all matches for this tournament type.
        Must be implemented by subclasses.
        
        Args:
            teams_per_poule: Number of teams per poule (for poule-based tournaments)
        
        Returns:
            List of Match objects
        """
        pass
    
    @abstractmethod
    def get_standings(self, phase: Optional[str] = None):
        """
        Get standings for this tournament.
        Must be implemented by subclasses.
        
        Args:
            phase: Optional phase to get standings for
        
        Returns:
            Standings data (format depends on tournament type)
        """
        pass
    
    def __repr__(self):
        return f"Tournament(id={self.id}, name='{self.name}', type='{self.tournament_type}')"


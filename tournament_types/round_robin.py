"""
Round Robin Tournament - everyone plays everyone (friendly tournament)
"""
import pandas as pd
from typing import List, Optional
from models.tournament import Tournament
from models.team import Team
from models.match import Match, MatchPhase


class RoundRobinTournament(Tournament):
    """Round-robin tournament: everyone plays against everyone"""
    
    def __init__(self, id=None, name="", sport_type="", tournament_type="round_robin",
                 team_type="single", has_consolation=False, created_at=None):
        super().__init__(id, name, sport_type, tournament_type, team_type, has_consolation, created_at)
    
    def generate_matches(self, teams_per_poule: int = 4) -> List[Match]:
        """
        Generate all matches for round-robin (everyone vs everyone, no poules)
        teams_per_poule parameter is ignored for round-robin
        """
        if not self.id:
            raise ValueError("Tournament must be saved before generating matches")
        
        teams = self.get_teams()
        if len(teams) < 2:
            return []
        
        matches = []
        # Generate all combinations (everyone vs everyone)
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                match = Match(
                    tournament_id=self.id,
                    phase=MatchPhase.POULE,  # Round-robin uses POULE phase
                    poule_id=None,  # No poules in round-robin
                    team1=teams[i],
                    team2=teams[j]
                )
                match.save()
                matches.append(match)
        
        return matches
    
    def get_standings(self, phase: Optional[str] = None) -> pd.DataFrame:
        """Get standings for round-robin tournament"""
        if not self.id:
            return pd.DataFrame()
        
        teams = self.get_teams()
        matches = self.get_matches(phase="poule")
        
        # Initialize stats for each team
        stats = {team.id: {
            'name': team.display_name,
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'points_for': 0,
            'points_against': 0
        } for team in teams}
        
        # Calculate stats from matches
        for match in matches:
            if not match.is_played:
                continue
            
            if match.team1.id in stats:
                stats[match.team1.id]['points_for'] += match.team1_score or 0
                stats[match.team1.id]['points_against'] += match.team2_score or 0
                if match.winner == match.team1:
                    stats[match.team1.id]['wins'] += 1
                elif match.loser == match.team1:
                    stats[match.team1.id]['losses'] += 1
                else:
                    stats[match.team1.id]['draws'] += 1
            
            if match.team2.id in stats:
                stats[match.team2.id]['points_for'] += match.team2_score or 0
                stats[match.team2.id]['points_against'] += match.team1_score or 0
                if match.winner == match.team2:
                    stats[match.team2.id]['wins'] += 1
                elif match.loser == match.team2:
                    stats[match.team2.id]['losses'] += 1
                else:
                    stats[match.team2.id]['draws'] += 1
        
        # Convert to DataFrame
        standings_data = []
        for team_id, stat in stats.items():
            standings_data.append({
                'Team': stat['name'],
                'Gewonnen': stat['wins'],
                'Verloren': stat['losses'],
                'Gelijk': stat['draws'],
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


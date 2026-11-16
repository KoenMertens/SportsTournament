"""
Default Tournament - Clubkampioenschap Tafeltennis
Poules (4 per poule, remainder 3) -> Knockout -> Optional Consolation
"""
import pandas as pd
from typing import List, Optional
from models.tournament import Tournament
from models.team import Team
from models.match import Match, MatchPhase
from utils.poules import get_or_create_poule, generate_poule_names
from utils.poule_distribution import distribute_teams_into_poules
from utils.bracket_generator import get_qualified_teams_from_poules, generate_knockout_bracket


class DefaultTournament(Tournament):
    """
    Default Tournament (Clubkampioenschap):
    - Fase 1: Poules (4 teams per poule, remainder in poules of 3)
    - Fase 2: Knockout (top teams from poules)
    - Fase 3: Consolation (optional, losers continue playing)
    """
    
    def __init__(self, id=None, name="", sport_type="", tournament_type="default_tournament",
                 team_type="single", has_consolation=False, created_at=None):
        super().__init__(id, name, sport_type, tournament_type, team_type, has_consolation, created_at)
    
    def generate_matches(self, teams_per_poule: int = 4):
        """
        Generate matches for default tournament:
        1. Create poules and distribute teams (4 per poule, remainder 3)
        2. Generate all poule matches (round-robin within each poule)
        Knockout and consolation matches are generated later when poules are finished
        """
        if not self.id:
            raise ValueError("Tournament must be saved before generating matches")
        
        teams = self.get_teams()
        if len(teams) < 3:
            raise ValueError(f"Minimum 3 teams required, got {len(teams)}")
        
        matches = []
        
        # Distribute teams into poules
        poule_distribution = distribute_teams_into_poules(len(teams), teams_per_poule)
        poule_names = generate_poule_names(len(poule_distribution))
        
        # Create poules and generate matches within each poule
        for poule_idx, poule_teams in enumerate(poule_distribution):
            poule_name = poule_names[poule_idx]
            poule_id = get_or_create_poule(self.id, MatchPhase.POULE.value, poule_name)
            
            # Generate round-robin matches within this poule
            for i in range(len(poule_teams)):
                for j in range(i + 1, len(poule_teams)):
                    team1 = teams[poule_teams[i]]
                    team2 = teams[poule_teams[j]]
                    
                    match = Match(
                        tournament_id=self.id,
                        phase=MatchPhase.POULE,
                        poule_id=poule_id,
                        team1=team1,
                        team2=team2
                    )
                    match.save()
                    matches.append(match)
        
        return matches
    
    def get_standings(self, phase: Optional[str] = None) -> pd.DataFrame:
        """Get standings for a specific phase (poule, knockout, or consolation)"""
        if not self.id:
            return pd.DataFrame()
        
        if phase == "poule" or phase is None:
            return self._get_poule_standings()
        elif phase == "knockout":
            return self._get_knockout_standings()
        elif phase == "consolation":
            return self._get_consolation_standings()
        else:
            return pd.DataFrame()
    
    def _get_poule_standings(self) -> pd.DataFrame:
        """Get standings per poule"""
        teams = self.get_teams()
        matches = [m for m in self.get_matches("poule") if m.is_played]
        
        # Get all poules
        from utils.poules import get_poules_by_tournament
        poules = get_poules_by_tournament(self.id, MatchPhase.POULE.value)
        
        # Initialize stats per poule
        poule_stats = {}
        for poule_id, poule_name in poules:
            poule_stats[poule_id] = {}
            # Get teams in this poule from matches
            for match in matches:
                if match.poule_id == poule_id:
                    if match.team1.id not in poule_stats[poule_id]:
                        poule_stats[poule_id][match.team1.id] = {
                            'name': match.team1.display_name,
                            'wins': 0, 'losses': 0, 'points_for': 0, 'points_against': 0
                        }
                    if match.team2.id not in poule_stats[poule_id]:
                        poule_stats[poule_id][match.team2.id] = {
                            'name': match.team2.display_name,
                            'wins': 0, 'losses': 0, 'points_for': 0, 'points_against': 0
                        }
        
        # Calculate stats from matches
        for match in matches:
            if match.poule_id not in poule_stats:
                continue
            
            stats = poule_stats[match.poule_id]
            
            if match.team1.id in stats:
                stats[match.team1.id]['points_for'] += match.team1_score or 0
                stats[match.team1.id]['points_against'] += match.team2_score or 0
                if match.winner == match.team1:
                    stats[match.team1.id]['wins'] += 1
                elif match.loser == match.team1:
                    stats[match.team1.id]['losses'] += 1
            
            if match.team2.id in stats:
                stats[match.team2.id]['points_for'] += match.team2_score or 0
                stats[match.team2.id]['points_against'] += match.team1_score or 0
                if match.winner == match.team2:
                    stats[match.team2.id]['wins'] += 1
                elif match.loser == match.team2:
                    stats[match.team2.id]['losses'] += 1
        
        # Combine all poule standings
        all_standings = []
        for poule_id, poule_name in poules:
            if poule_id not in poule_stats or not poule_stats[poule_id]:
                continue
            
            standings_data = []
            for team_id, stat in poule_stats[poule_id].items():
                standings_data.append({
                    'Poule': poule_name,
                    'Team': stat['name'],
                    'Gewonnen': stat['wins'],
                    'Verloren': stat['losses'],
                    'Punten Voor': stat['points_for'],
                    'Punten Tegen': stat['points_against'],
                    'Saldo': stat['points_for'] - stat['points_against']
                })
            
            # Sort by wins, then by saldo
            standings_data.sort(key=lambda x: (x['Gewonnen'], x['Saldo']), reverse=True)
            all_standings.extend(standings_data)
        
        df = pd.DataFrame(all_standings)
        if not df.empty:
            df.reset_index(drop=True, inplace=True)
            df.index = df.index + 1
        
        return df
    
    def all_poule_matches_played(self) -> bool:
        """Check if all poule matches have been played"""
        matches = self.get_matches("poule")
        if not matches:
            return False
        return all(m.is_played for m in matches)
    
    def generate_knockout_matches(self):
        """
        Generate knockout bracket matches based on poule results.
        Only works if all poule matches are played.
        """
        if not self.id:
            raise ValueError("Tournament must be saved")
        
        if not self.all_poule_matches_played():
            raise ValueError("All poule matches must be played before generating knockout bracket")
        
        # Get qualified teams (top 2 per poule)
        qualified = get_qualified_teams_from_poules(self.id, top_n=2)
        
        # Generate bracket
        matches = generate_knockout_bracket(self.id, qualified)
        
        # Save matches to database
        for match in matches:
            match.save()
        
        return matches
    
    def _get_knockout_standings(self) -> pd.DataFrame:
        """Get knockout phase matches and results"""
        matches = self.get_matches("knockout")
        if not matches:
            return pd.DataFrame()
        
        match_data = []
        for match in matches:
            match_data.append({
                'Team 1': match.team1.display_name if match.team1 else '?',
                'Score 1': match.team1_score if match.is_played else '-',
                'Score 2': match.team2_score if match.is_played else '-',
                'Team 2': match.team2.display_name if match.team2 else '?',
                'Status': 'Gespeeld' if match.is_played else 'Niet gespeeld'
            })
        
        return pd.DataFrame(match_data)
    
    def _get_consolation_standings(self) -> pd.DataFrame:
        """Get consolation phase matches and results"""
        matches = self.get_matches("consolation")
        if not matches:
            return pd.DataFrame()
        
        match_data = []
        for match in matches:
            match_data.append({
                'Team 1': match.team1.display_name if match.team1 else '?',
                'Score 1': match.team1_score if match.is_played else '-',
                'Score 2': match.team2_score if match.is_played else '-',
                'Team 2': match.team2.display_name if match.team2 else '?',
                'Status': 'Gespeeld' if match.is_played else 'Niet gespeeld'
            })
        
        return pd.DataFrame(match_data)


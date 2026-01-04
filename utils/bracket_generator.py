"""
Bracket generation utilities for knockout phase
"""
from typing import List, Tuple, Dict, Optional
from collections import defaultdict
from models.team import Team
from models.match import Match, MatchPhase
from database import get_connection


class TeamStats:
    """Statistics for a team in a poule"""
    def __init__(self, team: Team):
        self.team = team
        self.wins = 0  # Aantal gewonnen matches
        self.losses = 0
        self.sets_won = 0  # Aantal gewonnen sets
        self.sets_lost = 0
        self.points_for = 0  # Totaal punten voor (later toe te voegen)
        self.points_against = 0  # Totaal punten tegen (later toe te voegen)
    
    @property
    def sets_balance(self) -> int:
        """Sets saldo"""
        return self.sets_won - self.sets_lost
    
    @property
    def points_balance(self) -> int:
        """Punten saldo"""
        return self.points_for - self.points_against
    
    def __lt__(self, other):
        """Compare teams for ranking: wins > sets_won > points_balance"""
        if self.wins != other.wins:
            return self.wins < other.wins
        if self.sets_balance != other.sets_balance:
            return self.sets_balance < other.sets_balance
        return self.points_balance < other.points_balance
    
    def __repr__(self):
        return f"TeamStats({self.team.display_name}, W:{self.wins}, Sets:{self.sets_balance})"


def calculate_poule_standings(teams: List[Team], matches: List[Match]) -> List[Tuple[Team, TeamStats]]:
    """
    Calculate standings for teams in a poule based on matches.
    Ranking: 1. Wins, 2. Sets balance, 3. Points balance
    """
    stats_dict: Dict[int, TeamStats] = {team.id: TeamStats(team) for team in teams}
    
    for match in matches:
        if not match.is_played:
            continue
        
        # Update stats for team1
        if match.team1.id in stats_dict:
            stats = stats_dict[match.team1.id]
            stats.sets_won += match.team1_score or 0
            stats.sets_lost += match.team2_score or 0
            if match.winner == match.team1:
                stats.wins += 1
            elif match.loser == match.team1:
                stats.losses += 1
        
        # Update stats for team2
        if match.team2.id in stats_dict:
            stats = stats_dict[match.team2.id]
            stats.sets_won += match.team2_score or 0
            stats.sets_lost += match.team1_score or 0
            if match.winner == match.team2:
                stats.wins += 1
            elif match.loser == match.team2:
                stats.losses += 1
    
    # Sort by ranking criteria (reversed for descending)
    standings = [(team, stats_dict[team.id]) for team in teams if team.id in stats_dict]
    standings.sort(key=lambda x: x[1], reverse=True)
    
    return standings


def get_qualified_teams_from_poules(tournament_id: int, top_n: int = 2) -> List[Tuple[Team, str, TeamStats]]:
    """
    Get top N teams from each poule.
    Returns: List of (Team, poule_name, TeamStats) tuples, sorted by ranking (for bye selection)
    """
    from utils.poules import get_poules_by_tournament
    
    qualified = []
    poules = get_poules_by_tournament(tournament_id, MatchPhase.POULE.value)
    
    for poule_id, poule_name in poules:
        # Get teams in this poule from matches
        all_matches = Match.get_by_tournament(tournament_id, MatchPhase.POULE)
        poule_matches = [m for m in all_matches if m.poule_id == poule_id]
        
        # Get unique teams from matches
        team_ids = set()
        for match in poule_matches:
            team_ids.add(match.team1.id)
            team_ids.add(match.team2.id)
        
        teams = [Team.get_by_id(tid) for tid in team_ids if Team.get_by_id(tid)]
        if not teams:
            continue
        
        # Calculate standings for this poule
        standings = calculate_poule_standings(teams, poule_matches)
        
        # Take top N teams from this poule
        for i, (team, stats) in enumerate(standings[:top_n]):
            qualified.append((team, poule_name, stats))
    
    # Sort all qualified teams by their stats for bye selection (best teams first)
    qualified.sort(key=lambda x: x[2], reverse=True)
    
    return qualified


def generate_knockout_bracket(tournament_id: int, qualified_teams: List[Tuple[Team, str, TeamStats]]) -> List[Match]:
    """
    Generate knockout bracket matches.
    
    Logic:
    - 4 teams (2 poules): A1 vs B2, B1 vs A2
    - 6 teams (3 poules): 2 best get bye, 4 others play quarterfinals
    - 8 teams (4 poules): A1 vs D2, B1 vs C2, C1 vs B2, D1 vs A2
    - 10+ teams: extra round(s) needed
    
    Returns: List of Match objects (not yet saved)
    """
    num_teams = len(qualified_teams)
    
    if num_teams < 2:
        return []
    
    matches = []
    
    # Group teams by poule
    poule_groups: Dict[str, List[Tuple[Team, int]]] = {}  # poule_name -> [(team, rank_in_poule)]
    for idx, (team, poule_name) in enumerate(qualified_teams):
        if poule_name not in poule_groups:
            poule_groups[poule_name] = []
        # Rank in poule: first 2 are rank 1, next 2 are rank 2, etc.
        rank = (idx % 2) + 1  # Simplified: assume sorted by poule
        poule_groups[poule_name].append((team, rank))
    
    # Track teams by poule (with their rank: 1st or 2nd in poule)
    poule_teams: Dict[str, List[Team]] = defaultdict(list)
    for team, poule_name, stats in qualified_teams:
        poule_teams[poule_name].append(team)
    
    # Determine bracket structure
    if num_teams == 4:
        # 2 poules: A1 vs B2, B1 vs A2
        poule_names = sorted(poule_teams.keys())
        if len(poule_names) == 2:
            a_teams = poule_teams[poule_names[0]]
            b_teams = poule_teams[poule_names[1]]
            if len(a_teams) >= 1 and len(b_teams) >= 2:
                matches.append(Match(
                    tournament_id=tournament_id,
                    phase=MatchPhase.KNOCKOUT,
                    team1=a_teams[0],  # A1
                    team2=b_teams[1]   # B2
                ))
            if len(a_teams) >= 2 and len(b_teams) >= 1:
                matches.append(Match(
                    tournament_id=tournament_id,
                    phase=MatchPhase.KNOCKOUT,
                    team1=b_teams[0],  # B1
                    team2=a_teams[1]   # A2
                ))
        else:
            # Fallback: first vs last, second vs second-last
            matches.append(Match(
                tournament_id=tournament_id,
                phase=MatchPhase.KNOCKOUT,
                team1=qualified_teams[0][0],
                team2=qualified_teams[3][0]
            ))
            matches.append(Match(
                tournament_id=tournament_id,
                phase=MatchPhase.KNOCKOUT,
                team1=qualified_teams[1][0],
                team2=qualified_teams[2][0]
            ))
    
    elif num_teams == 6:
        # 3 poules: 2 best overall get bye, 4 others play quarterfinals
        # Teams are already sorted by stats, so first 2 get bye
        # Remaining 4 play: 3 vs 6, 4 vs 5
        matches.append(Match(
            tournament_id=tournament_id,
            phase=MatchPhase.KNOCKOUT,
            team1=qualified_teams[2][0],  # 3rd best overall
            team2=qualified_teams[5][0]   # 6th best overall
        ))
        matches.append(Match(
            tournament_id=tournament_id,
            phase=MatchPhase.KNOCKOUT,
            team1=qualified_teams[3][0],  # 4th best overall
            team2=qualified_teams[4][0]   # 5th best overall
        ))
    
    elif num_teams == 8:
        # 4 poules: A1 vs D2, B1 vs C2, C1 vs B2, D1 vs A2
        poule_names = sorted(poule_teams.keys())
        if len(poule_names) == 4:
            teams_by_poule = [poule_teams[pn] for pn in poule_names]
            # A vs D
            matches.append(Match(
                tournament_id=tournament_id,
                phase=MatchPhase.KNOCKOUT,
                team1=teams_by_poule[0][0],  # A1
                team2=teams_by_poule[3][1] if len(teams_by_poule[3]) > 1 else teams_by_poule[3][0]  # D2
            ))
            matches.append(Match(
                tournament_id=tournament_id,
                phase=MatchPhase.KNOCKOUT,
                team1=teams_by_poule[3][0],  # D1
                team2=teams_by_poule[0][1] if len(teams_by_poule[0]) > 1 else teams_by_poule[0][0]  # A2
            ))
            # B vs C
            matches.append(Match(
                tournament_id=tournament_id,
                phase=MatchPhase.KNOCKOUT,
                team1=teams_by_poule[1][0],  # B1
                team2=teams_by_poule[2][1] if len(teams_by_poule[2]) > 1 else teams_by_poule[2][0]  # C2
            ))
            matches.append(Match(
                tournament_id=tournament_id,
                phase=MatchPhase.KNOCKOUT,
                team1=teams_by_poule[2][0],  # C1
                team2=teams_by_poule[1][1] if len(teams_by_poule[1]) > 1 else teams_by_poule[1][0]  # B2
            ))
        else:
            # Fallback: standard pairing
            for i in range(4):
                matches.append(Match(
                    tournament_id=tournament_id,
                    phase=MatchPhase.KNOCKOUT,
                    team1=qualified_teams[i][0],
                    team2=qualified_teams[7-i][0]
                ))
    
    else:
        # For other numbers, create first round (will need more rounds later)
        # Pair teams: first vs last, second vs second-last, etc.
        for i in range(num_teams // 2):
            matches.append(Match(
                tournament_id=tournament_id,
                phase=MatchPhase.KNOCKOUT,
                team1=qualified_teams[i][0],
                team2=qualified_teams[num_teams - 1 - i][0]
            ))
    
    return matches


def generate_knockout_round(tournament_id: int, previous_round_winners: List[Team], round_name: str) -> List[Match]:
    """
    Generate next round of knockout bracket from previous round winners.
    """
    num_teams = len(previous_round_winners)
    
    if num_teams < 2:
        return []
    
    matches = []
    # Pair teams: first vs last, second vs second-last, etc.
    for i in range(num_teams // 2):
        matches.append(Match(
            tournament_id=tournament_id,
            phase=MatchPhase.KNOCKOUT,
            team1=previous_round_winners[i],
            team2=previous_round_winners[num_teams - 1 - i]
        ))
    
    return matches


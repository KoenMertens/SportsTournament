"""
Poule distribution utilities - handles team distribution into poules
"""
from typing import List, Tuple


def distribute_teams_into_poules(num_teams: int, teams_per_poule: int = 4) -> List[List[int]]:
    """
    Distribute teams into poules.
    Rules:
    - Minimum 3 teams required
    - Default 4 teams per poule
    - Special case: 5 teams = 1 poule of 5 (only exception)
    - Otherwise: as many poules of 4 as possible, remainder in poules of 3
    - Never create poules of 5+ (except the 5 teams case)
    
    Args:
        num_teams: Total number of teams
        teams_per_poule: Preferred teams per poule (default 4, ignored for 5 teams case)
    
    Returns:
        List of poules, each poule is a list of team indices (0-based)
    
    Examples:
        distribute_teams_into_poules(5) -> [[0,1,2,3,4]]  # 1 poule van 5
        distribute_teams_into_poules(6) -> [[0,1,2], [3,4,5]]  # 2 poules van 3
        distribute_teams_into_poules(7) -> [[0,1,2,3], [4,5,6]]  # 1 poule van 4, 1 poule van 3
        distribute_teams_into_poules(8) -> [[0,1,2,3], [4,5,6,7]]  # 2 poules van 4
        distribute_teams_into_poules(9) -> [[0,1,2], [3,4,5], [6,7,8]]  # 3 poules van 3
        distribute_teams_into_poules(10) -> [[0,1,2,3], [4,5,6], [7,8,9]]  # 1 poule van 4, 2 poules van 3
    """
    if num_teams < 3:
        raise ValueError(f"Minimum 3 teams required, got {num_teams}")
    
    # Special case: 5 teams = 1 poule of 5
    if num_teams == 5:
        return [[0, 1, 2, 3, 4]]
    
    poules = []
    team_idx = 0
    
    # Calculate how many full poules of 4 we can make
    num_full_poules = num_teams // teams_per_poule
    remainder = num_teams % teams_per_poule
    
    # If remainder == 1, we need to avoid creating a poule of 5
    # Strategy: reduce one poule of 4, then we have 4+1=5 teams left
    # But we can't make poules of 5, so we make 1 poule of 4 and distribute the remaining 1
    # Actually, if remainder == 1, we should convert one poule of 4 to poules of 3
    # Example: 9 teams = 2 poules of 4 (8) + 1 remainder -> convert to 3 poules of 3
    if remainder == 1 and num_full_poules > 0:
        # Convert one poule of 4 into poules of 3
        # Instead of: num_full_poules poules of 4 + 1 team
        # We do: (num_full_poules-1) poules of 4 + 4 teams (from converted poule) + 1 team = 5 teams
        # But 5 teams = special case (1 poule of 5), so we avoid that
        # Better: convert to all poules of 3
        # For 9: 3 poules of 3 = 9 teams
        num_full_poules = 0
        remainder = num_teams
    
    # If remainder == 2, we can't make poules of 3, so we need to adjust
    # Example: 6 teams = 1 poule of 4 + 2 remainder -> should be 2 poules of 3
    if remainder == 2 and num_full_poules > 0:
        # Convert one poule of 4, now we have 4+2=6 teams = 2 poules of 3
        num_full_poules -= 1
        remainder = 6
    
    # Create full poules of 4
    for _ in range(num_full_poules):
        poule = list(range(team_idx, team_idx + teams_per_poule))
        poules.append(poule)
        team_idx += teams_per_poule
    
    # Handle remainder - create poules of 3
    while team_idx < num_teams:
        remaining = num_teams - team_idx
        if remaining >= 3:
            # Create poule of 3
            poules.append([team_idx, team_idx + 1, team_idx + 2])
            team_idx += 3
        elif remaining == 2:
            # Only 2 teams left - shouldn't happen with proper logic, but handle it
            poules.append([team_idx, team_idx + 1])
            break
        else:
            # Only 1 team left - shouldn't happen, but handle it
            # This means we have a logic error, but add to last poule or create single
            if len(poules) > 0:
                poules[-1].append(team_idx)
            else:
                poules.append([team_idx])
            break
    
    return poules


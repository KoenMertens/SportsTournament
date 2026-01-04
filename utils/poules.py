"""
Poule management utilities
"""
import sqlite3
from typing import Optional, List, Tuple
from database import get_connection


def create_poule(tournament_id: int, phase: str, name: str) -> int:
    """Create a poule and return its ID"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO poules (tournament_id, phase, name)
        VALUES (?, ?, ?)
    ''', (tournament_id, phase, name))
    poule_id = c.lastrowid
    conn.commit()
    conn.close()
    return poule_id


def get_poule_id(tournament_id: int, phase: str, name: str) -> Optional[int]:
    """Get poule ID by tournament, phase and name"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT id FROM poules
        WHERE tournament_id = ? AND phase = ? AND name = ?
    ''', (tournament_id, phase, name))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def get_or_create_poule(tournament_id: int, phase: str, name: str) -> int:
    """Get poule ID if exists, otherwise create it"""
    poule_id = get_poule_id(tournament_id, phase, name)
    if poule_id:
        return poule_id
    return create_poule(tournament_id, phase, name)


def get_poules_by_tournament(tournament_id: int, phase: Optional[str] = None) -> List[Tuple]:
    """Get all poules for a tournament, optionally filtered by phase"""
    conn = get_connection()
    c = conn.cursor()
    
    if phase:
        c.execute('''
            SELECT id, name FROM poules
            WHERE tournament_id = ? AND phase = ?
            ORDER BY name
        ''', (tournament_id, phase))
    else:
        c.execute('''
            SELECT id, name FROM poules
            WHERE tournament_id = ?
            ORDER BY name
        ''', (tournament_id,))
    
    rows = c.fetchall()
    conn.close()
    return rows


def generate_poule_names(num_poules: int) -> List[str]:
    """Generate poule names (A, B, C, ...)"""
    return [chr(65 + i) for i in range(num_poules)]  # 65 = 'A' in ASCII


"""
lore_fuzzy.py

Fuzzy matching utility for LoreBuilder character name queries.
Uses RapidFuzz for string similarity.
"""
from typing import Set, Optional, Tuple
from rapidfuzz import process, fuzz


def find_best_character_match(query: str, characters: Set[str], min_ratio: int = 80) -> Tuple[Optional[str], list]:
    """
    Given a query (user's character name) and a set of known characters,
    return a best match and a list of close matches using fuzzy string matching.
    Args:
        query: User-supplied character name (str)
        characters: Set of character names from lore
        min_ratio: Minimum similarity (0-100) to consider acceptable match
    Returns:
        (best_match, suggestions)
        best_match: string if a sufficiently similar character is found, else None
        suggestions: list of alternative close names (sorted best to worst match)
    """
    if not characters or not query:
        return None, []
    # Use RapidFuzz extract and find top matches
    best_matches = process.extract(
        query,
        list(characters),
        scorer=fuzz.ratio,
        limit=3 # return top 3 for suggestions
    )
    close_matches = [name for name, score, _ in best_matches if score >= min_ratio]
    best_match = close_matches[0] if close_matches else None
    return best_match, close_matches

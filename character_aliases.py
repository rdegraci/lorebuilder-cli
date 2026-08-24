"""
character_aliases.py

Persistent display-name aliases for characters extracted from lore.
Maps lore names (spaCy NER) to preferred chat names without editing lore text.
"""
import sqlite3
from typing import Dict, List, Optional, Set, Tuple

from constants import DEFAULT_CHAT_DB_FILE, ERROR_DB_INIT_FAILED
from lore_fuzzy import find_best_character_match


class CharacterAliasService:
    """SQLite-backed lore_name -> display_name mappings."""

    def __init__(self, db_file: Optional[str] = None):
        self.db_file = db_file or DEFAULT_CHAT_DB_FILE

    def initialize_db(self) -> None:
        """Create the character_aliases table if it does not exist."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS character_aliases (
                        lore_name TEXT PRIMARY KEY,
                        display_name TEXT NOT NULL
                    )
                    """
                )
                conn.commit()
        except sqlite3.Error as e:
            raise sqlite3.Error(f"{ERROR_DB_INIT_FAILED}: {e}")

    def set_alias(self, lore_name: str, display_name: str) -> None:
        """Map a lore name to a display/chat name."""
        self.initialize_db()
        lore_name = lore_name.strip()
        display_name = display_name.strip()
        if not lore_name or not display_name:
            raise ValueError("Lore name and display name cannot be empty")

        with sqlite3.connect(self.db_file) as conn:
            conn.execute(
                """
                INSERT INTO character_aliases (lore_name, display_name)
                VALUES (?, ?)
                ON CONFLICT(lore_name) DO UPDATE SET display_name=excluded.display_name
                """,
                (lore_name, display_name),
            )
            conn.commit()

    def get_all(self) -> Dict[str, str]:
        """Return all lore_name -> display_name mappings."""
        self.initialize_db()
        with sqlite3.connect(self.db_file) as conn:
            rows = conn.execute(
                "SELECT lore_name, display_name FROM character_aliases"
            ).fetchall()
        return {lore_name: display_name for lore_name, display_name in rows}

    def get_display_name(self, lore_name: str, aliases: Optional[Dict[str, str]] = None) -> str:
        """Return the display name for a lore name, or the lore name itself."""
        mapping = aliases if aliases is not None else self.get_all()
        return mapping.get(lore_name, lore_name)

    def build_effective_characters(
        self,
        characters_in_lore: Set[str],
        aliases: Optional[Dict[str, str]] = None,
    ) -> Set[str]:
        """Return display names used for list_characters and chat resolution."""
        mapping = aliases if aliases is not None else self.get_all()
        return {mapping.get(name, name) for name in characters_in_lore}

    def lore_search_terms(
        self,
        display_name: str,
        characters_in_lore: Set[str],
        aliases: Optional[Dict[str, str]] = None,
    ) -> List[str]:
        """Terms to include when querying lore for a character."""
        mapping = aliases if aliases is not None else self.get_all()
        terms = [display_name]
        for lore_name, alias_display in mapping.items():
            if alias_display == display_name and lore_name in characters_in_lore:
                terms.append(lore_name)
        if display_name in characters_in_lore and display_name not in terms:
            terms.append(display_name)
        return list(dict.fromkeys(terms))

    def find_lore_name(
        self,
        name: str,
        characters_in_lore: Set[str],
        aliases: Optional[Dict[str, str]] = None,
    ) -> Optional[str]:
        """Resolve a user-supplied name to its underlying lore name."""
        mapping = aliases if aliases is not None else self.get_all()
        query = name.strip()
        if not query:
            return None

        if query in characters_in_lore:
            return query
        if query in mapping:
            return query

        for lore_name, display_name in mapping.items():
            if display_name.lower() == query.lower():
                return lore_name

        effective = self.build_effective_characters(characters_in_lore, mapping)
        best_match, _ = find_best_character_match(query, effective)
        if best_match:
            for lore_name in characters_in_lore:
                if mapping.get(lore_name, lore_name) == best_match:
                    return lore_name
            if best_match in characters_in_lore:
                return best_match

        best_match, _ = find_best_character_match(query, characters_in_lore)
        if best_match:
            return best_match

        return None

    def resolve_display_name(
        self,
        query: str,
        characters_in_lore: Set[str],
        aliases: Optional[Dict[str, str]] = None,
    ) -> Tuple[Optional[str], List[str]]:
        """
        Resolve user input to a display/chat name.

        Returns:
            (display_name, close_matches)
        """
        mapping = aliases if aliases is not None else self.get_all()
        effective = self.build_effective_characters(characters_in_lore, mapping)
        if not query or not effective:
            return None, []

        query_stripped = query.strip()
        for display_name in effective:
            if display_name.lower() == query_stripped.lower():
                return display_name, [display_name]

        for lore_name, display_name in mapping.items():
            if lore_name.lower() == query_stripped.lower() and lore_name in characters_in_lore:
                return display_name, [display_name]

        best_match, close_matches = find_best_character_match(query_stripped, effective)
        if best_match:
            return best_match, close_matches

        best_lore, close_lore = find_best_character_match(query_stripped, characters_in_lore)
        if best_lore:
            display = mapping.get(best_lore, best_lore)
            return display, close_lore

        return None, close_matches or close_lore


_alias_service = CharacterAliasService()


def initialize_db() -> None:
    """Create alias tables if they do not exist."""
    return _alias_service.initialize_db()


def set_alias(lore_name: str, display_name: str) -> None:
    """Map a lore name to a display/chat name."""
    return _alias_service.set_alias(lore_name, display_name)


def get_all() -> Dict[str, str]:
    """Return all lore_name -> display_name mappings."""
    return _alias_service.get_all()


def build_effective_characters(
    characters_in_lore: Set[str],
    aliases: Optional[Dict[str, str]] = None,
) -> Set[str]:
    """Return display names used for list_characters and chat resolution."""
    return _alias_service.build_effective_characters(characters_in_lore, aliases)


def lore_search_terms(
    display_name: str,
    characters_in_lore: Set[str],
    aliases: Optional[Dict[str, str]] = None,
) -> List[str]:
    """Terms to include when querying lore for a character."""
    return _alias_service.lore_search_terms(display_name, characters_in_lore, aliases)


def find_lore_name(
    name: str,
    characters_in_lore: Set[str],
    aliases: Optional[Dict[str, str]] = None,
) -> Optional[str]:
    """Resolve a user-supplied name to its underlying lore name."""
    return _alias_service.find_lore_name(name, characters_in_lore, aliases)


def resolve_display_name(
    query: str,
    characters_in_lore: Set[str],
    aliases: Optional[Dict[str, str]] = None,
) -> Tuple[Optional[str], List[str]]:
    """Resolve user input to a display/chat name."""
    return _alias_service.resolve_display_name(query, characters_in_lore, aliases)

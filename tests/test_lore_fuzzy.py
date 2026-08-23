"""Tests for lore_fuzzy character name matching."""
from lore_fuzzy import find_best_character_match


CHARACTERS = {"Mara", "The Mage of the Lake", "Lord Ardelune"}


def test_exact_match():
    match, suggestions = find_best_character_match("Mara", CHARACTERS)
    assert match == "Mara"
    assert "Mara" in suggestions


def test_typo_fuzzy_match():
    match, suggestions = find_best_character_match("Mra", CHARACTERS)
    assert match == "Mara"
    assert suggestions


def test_close_fuzzy_match():
    match, suggestions = find_best_character_match("Mage of the Lake", CHARACTERS)
    assert match == "The Mage of the Lake"
    assert suggestions


def test_no_match_returns_none():
    match, suggestions = find_best_character_match("Unknown Hero", CHARACTERS, min_ratio=95)
    assert match is None
    assert suggestions == []


def test_empty_query_returns_none():
    match, suggestions = find_best_character_match("", CHARACTERS)
    assert match is None
    assert suggestions == []


def test_empty_characters_returns_none():
    match, suggestions = find_best_character_match("Mara", set())
    assert match is None
    assert suggestions == []

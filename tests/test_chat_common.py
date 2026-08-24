"""Tests for shared chat helper functions."""
import importlib

import character_aliases


def test_build_lore_query_includes_lore_and_display_names(monkeypatch):
    chat_common = importlib.import_module("commands.chat_common")

    monkeypatch.setattr(
        character_aliases,
        "get_all",
        lambda: {"Warlord": "Valeria"},
    )
    monkeypatch.setattr(
        character_aliases,
        "lore_search_terms",
        lambda display_name, characters_in_lore, aliases=None: ["Valeria", "Warlord"],
    )

    query = chat_common.build_lore_query(
        "Valeria",
        "Who rules?",
        {"Warlord"},
    )

    assert query == "Valeria Warlord Who rules?"

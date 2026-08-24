"""Tests for character alias persistence and resolution."""
import pytest

from character_aliases import CharacterAliasService


@pytest.fixture
def alias_service(tmp_path):
    service = CharacterAliasService(db_file=str(tmp_path / "aliases.db"))
    service.initialize_db()
    return service


def test_set_alias_and_get_all(alias_service):
    alias_service.set_alias("Warlord", "Valeria")

    assert alias_service.get_all() == {"Warlord": "Valeria"}


def test_build_effective_characters_applies_aliases(alias_service):
    alias_service.set_alias("Warlord", "Valeria")

    effective = alias_service.build_effective_characters({"Warlord", "Mara"})

    assert effective == {"Valeria", "Mara"}


def test_lore_search_terms_includes_both_names(alias_service):
    alias_service.set_alias("Warlord", "Valeria")

    terms = alias_service.lore_search_terms("Valeria", {"Warlord", "Mara"})

    assert terms == ["Valeria", "Warlord"]


def test_resolve_display_name_from_lore_name(alias_service):
    alias_service.set_alias("Warlord", "Valeria")

    display_name, _ = alias_service.resolve_display_name(
        "Warlord",
        {"Warlord"},
        alias_service.get_all(),
    )

    assert display_name == "Valeria"


def test_resolve_display_name_from_display_name(alias_service):
    alias_service.set_alias("Warlord", "Valeria")

    display_name, _ = alias_service.resolve_display_name(
        "Valeria",
        {"Warlord"},
        alias_service.get_all(),
    )

    assert display_name == "Valeria"


def test_find_lore_name_from_display_name(alias_service):
    alias_service.set_alias("Warlord", "Valeria")

    lore_name = alias_service.find_lore_name(
        "Valeria",
        {"Warlord"},
        alias_service.get_all(),
    )

    assert lore_name == "Warlord"

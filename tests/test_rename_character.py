"""Tests for rename_character command handler."""
import importlib

import character_aliases
import chat_history


def _rename_character_module():
    return importlib.import_module("commands.rename_character")


def test_rename_character_requires_two_names(initialized_lore, capture_rprint):
    capture, buffer = capture_rprint
    rename_character = _rename_character_module()
    capture(rename_character)

    rename_character.handle(["Warlord"], initialized_lore["context"])

    assert "Usage: rename_character" in buffer.getvalue()


def test_rename_character_sets_alias_and_migrates_session(
    initialized_lore, capture_rprint, monkeypatch, tmp_path
):
    capture, buffer = capture_rprint
    rename_character = _rename_character_module()
    capture(rename_character)

    db_file = str(tmp_path / "chat.db")
    alias_service = character_aliases.CharacterAliasService(db_file=db_file)
    alias_service.initialize_db()
    chat_service = chat_history.ChatHistoryService(db_file=db_file)
    chat_service.initialize_db()
    alias_service.initialize_db()

    session_id = chat_service.get_or_create_session("Warlord")
    chat_service.add_message(session_id, "user", "Hello")

    monkeypatch.setattr(character_aliases, "_alias_service", alias_service)
    monkeypatch.setattr(character_aliases, "set_alias", alias_service.set_alias)
    monkeypatch.setattr(character_aliases, "get_all", alias_service.get_all)
    monkeypatch.setattr(chat_history, "_chat_history_service", chat_service)
    monkeypatch.setattr(
        chat_history,
        "rename_session_character",
        chat_service.rename_session_character,
    )

    context = {"characters_in_lore": {"Warlord"}}
    rename_character.handle(["Warlord", "Valeria"], context)

    output = buffer.getvalue()
    assert "Warlord → Valeria" in output
    assert alias_service.get_all() == {"Warlord": "Valeria"}

    sessions = chat_service.list_sessions("Valeria")
    assert len(sessions) == 1
    assert chat_service.get_history(sessions[0][0]) == [("user", "Hello")]


def test_rename_character_rejects_unknown_character(
    initialized_lore, capture_rprint, monkeypatch, tmp_path
):
    capture, buffer = capture_rprint
    rename_character = _rename_character_module()
    capture(rename_character)

    db_file = str(tmp_path / "chat.db")
    alias_service = character_aliases.CharacterAliasService(db_file=db_file)
    alias_service.initialize_db()
    monkeypatch.setattr(character_aliases, "_alias_service", alias_service)
    monkeypatch.setattr(character_aliases, "get_all", alias_service.get_all)

    rename_character.handle(["Unknown", "Valeria"], {"characters_in_lore": {"Warlord"}})

    assert "not mentioned in any world lore" in buffer.getvalue()


def test_list_characters_shows_alias_with_lore_hint(capture_rprint, monkeypatch):
    capture, buffer = capture_rprint
    list_characters = importlib.import_module("commands.list_characters")
    capture(list_characters)

    monkeypatch.setattr(
        character_aliases,
        "get_all",
        lambda: {"Warlord": "Valeria"},
    )
    monkeypatch.setattr(
        character_aliases,
        "build_effective_characters",
        lambda characters, aliases=None: {"Valeria"},
    )

    list_characters.handle([], {"characters_in_lore": {"Warlord"}})

    output = buffer.getvalue()
    assert "Valeria" in output
    assert "lore: Warlord" in output

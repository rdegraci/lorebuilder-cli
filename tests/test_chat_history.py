"""Tests for SQLite chat history service."""
import pytest

from constants import ERROR_EMPTY_CHARACTER_NAME, ERROR_EMPTY_MESSAGE, ERROR_INVALID_LIMIT, ERROR_INVALID_ROLE


def test_get_or_create_session_creates_new_session(chat_service):
    session_id = chat_service.get_or_create_session("Mara")

    assert isinstance(session_id, int)
    sessions = chat_service.list_sessions("Mara")
    assert len(sessions) == 1
    assert sessions[0][1] == "Mara"


def test_get_or_create_session_reuses_existing_session(chat_service):
    first_id = chat_service.get_or_create_session("Mara")
    second_id = chat_service.get_or_create_session("Mara")

    assert first_id == second_id


def test_add_message_and_get_history(chat_service):
    session_id = chat_service.get_or_create_session("Mara")
    chat_service.add_message(session_id, "user", "Hello Mara")
    chat_service.add_message(session_id, "character", "Greetings, traveler.")

    history = chat_service.get_history(session_id)

    assert history == [
        ("user", "Hello Mara"),
        ("character", "Greetings, traveler."),
    ]


def test_rename_session_character_updates_session_key(chat_service):
    session_id = chat_service.get_or_create_session("Warlord")
    chat_service.add_message(session_id, "user", "Hello")

    updated = chat_service.rename_session_character("Warlord", "Valeria")

    assert updated == 1
    assert chat_service.list_sessions("Warlord") == []
    sessions = chat_service.list_sessions("Valeria")
    assert len(sessions) == 1
    assert sessions[0][0] == session_id


def test_reset_history_clears_messages_but_keeps_session(chat_service):
    session_id = chat_service.get_or_create_session("Mara")
    chat_service.add_message(session_id, "user", "Hello")

    chat_service.reset_history(session_id)

    assert chat_service.get_history(session_id) == []
    assert chat_service.list_sessions("Mara")


def test_delete_session_removes_session(chat_service):
    session_id = chat_service.get_or_create_session("Mara")
    chat_service.add_message(session_id, "user", "Hello")

    chat_service.delete_session(session_id)

    assert chat_service.list_sessions("Mara") == []


def test_export_history_returns_message_dicts(chat_service):
    session_id = chat_service.get_or_create_session("Mara")
    chat_service.add_message(session_id, "user", "Hello")

    exported = chat_service.export_history(session_id)

    assert len(exported) == 1
    assert exported[0]["role"] == "user"
    assert exported[0]["message"] == "Hello"
    assert exported[0]["timestamp"]


def test_list_sessions_filters_by_character(chat_service):
    chat_service.get_or_create_session("Mara")
    chat_service.get_or_create_session("Arin")

    mara_sessions = chat_service.list_sessions("Mara")
    all_sessions = chat_service.list_sessions()

    assert len(mara_sessions) == 1
    assert mara_sessions[0][1] == "Mara"
    assert len(all_sessions) == 2


def test_get_or_create_session_rejects_empty_character(chat_service):
    with pytest.raises(ValueError, match=ERROR_EMPTY_CHARACTER_NAME):
        chat_service.get_or_create_session("")


def test_add_message_rejects_invalid_role(chat_service):
    session_id = chat_service.get_or_create_session("Mara")

    with pytest.raises(ValueError, match=ERROR_INVALID_ROLE):
        chat_service.add_message(session_id, "narrator", "Hello")


def test_add_message_rejects_empty_message(chat_service):
    session_id = chat_service.get_or_create_session("Mara")

    with pytest.raises(ValueError, match=ERROR_EMPTY_MESSAGE):
        chat_service.add_message(session_id, "user", "   ")


def test_get_history_rejects_invalid_limit(chat_service):
    session_id = chat_service.get_or_create_session("Mara")

    with pytest.raises(ValueError, match=ERROR_INVALID_LIMIT):
        chat_service.get_history(session_id, limit=0)

"""Tests for chat_as command handler."""
import importlib
from types import SimpleNamespace
from unittest.mock import MagicMock

import litellm
import lore


def _chat_as_module():
    return importlib.import_module("commands.chat_as")


def test_chat_as_requires_initialized_lore_service(capture_rprint):
    capture, buffer = capture_rprint
    chat_as = _chat_as_module()
    capture(chat_as)
    lore._lore_service = None

    chat_as.handle(["Mara", "Hello"], {"characters_in_lore": {"Mara"}})

    assert "Lore service is not initialized" in buffer.getvalue()


def test_chat_as_requires_character_and_message(initialized_lore, capture_rprint):
    capture, buffer = capture_rprint
    chat_as = _chat_as_module()
    capture(chat_as)

    chat_as.handle(["Mara"], initialized_lore["context"])

    assert "Usage: chat_as" in buffer.getvalue()


def test_chat_as_rejects_unknown_character(initialized_lore, capture_rprint):
    capture, buffer = capture_rprint
    chat_as = _chat_as_module()
    capture(chat_as)

    chat_as.handle(
        ["Unknown", "Hello"],
        {"characters_in_lore": {"Mara"}},
    )

    output = buffer.getvalue()
    assert "not mentioned in any world lore" in output
    assert "list_characters" in output


def test_chat_as_fuzzy_matches_character_name(
    initialized_lore, capture_rprint, mock_llm_response, monkeypatch
):
    capture, buffer = capture_rprint
    chat_as = _chat_as_module()
    capture(chat_as)

    session_calls = {"session_id": 1}

    monkeypatch.setattr(
        chat_as.chat_history,
        "get_or_create_session",
        lambda character: session_calls["session_id"],
    )
    monkeypatch.setattr(chat_as.chat_history, "add_message", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        chat_as.chat_history,
        "get_history",
        lambda session_id, limit=20: [("user", "Hello")],
    )
    monkeypatch.setattr(
        chat_as.lore,
        "query_lore_internal",
        lambda query, n_results=3: ["Mara guards the lake."],
    )
    monkeypatch.setattr(litellm, "completion", lambda **kwargs: mock_llm_response)

    chat_as.handle(
        ["Mra", "Who are you?"],
        {"characters_in_lore": {"Mara"}},
    )

    output = buffer.getvalue()
    assert "Interpreting 'Mra' as 'Mara'" in output
    assert "Mara:" in output
    assert "Generated festival lore." in output


def test_chat_as_supports_quoted_multi_word_names(
    initialized_lore, capture_rprint, mock_llm_response, monkeypatch
):
    capture, buffer = capture_rprint
    chat_as = _chat_as_module()
    capture(chat_as)

    captured_character = {}

    monkeypatch.setattr(
        chat_as.chat_history,
        "get_or_create_session",
        lambda character: captured_character.setdefault("name", character) or 1,
    )
    monkeypatch.setattr(chat_as.chat_history, "add_message", lambda *args, **kwargs: None)
    monkeypatch.setattr(chat_as.chat_history, "get_history", lambda session_id, limit=20: [])
    monkeypatch.setattr(chat_as.lore, "query_lore_internal", lambda query, n_results=3: [])
    monkeypatch.setattr(litellm, "completion", lambda **kwargs: mock_llm_response)

    chat_as.handle(
        ['"The', 'Mage', 'of', 'the', 'Lake"', "Who visits at midnight?"],
        {"characters_in_lore": {"The Mage of the Lake"}},
    )

    assert captured_character["name"] == "The Mage of the Lake"
    assert "The Mage of the Lake:" in buffer.getvalue()


def test_chat_as_builds_system_prompt_from_config(
    initialized_lore, mock_llm_response, monkeypatch
):
    chat_as = _chat_as_module()
    initialized_lore["service"].config["chat_prompt_template"] = (
        "You are {character_name}. Lore: {context}"
    )
    captured = {}

    monkeypatch.setattr(chat_as.chat_history, "get_or_create_session", lambda character: 1)
    monkeypatch.setattr(chat_as.chat_history, "add_message", lambda *args, **kwargs: None)
    monkeypatch.setattr(chat_as.chat_history, "get_history", lambda session_id, limit=20: [])
    monkeypatch.setattr(
        chat_as.lore,
        "query_lore_internal",
        lambda query, n_results=3: ["Lake lore"],
    )

    def fake_completion(**kwargs):
        captured["messages"] = kwargs["messages"]
        return mock_llm_response

    monkeypatch.setattr(litellm, "completion", fake_completion)

    chat_as.handle(
        ["Mara", "Hello"],
        {"characters_in_lore": {"Mara"}},
    )

    system_prompt = captured["messages"][0]["content"]
    assert "You are Mara." in system_prompt
    assert "Lake lore" in system_prompt

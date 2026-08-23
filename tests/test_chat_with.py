"""Tests for chat_with command handler."""
import importlib
from unittest.mock import MagicMock

import commands.chat_common as chat_common
import lore


def _chat_with_module():
    return importlib.import_module("commands.chat_with")


def test_chat_with_requires_character_name(initialized_lore, capture_rprint):
    capture, buffer = capture_rprint
    chat_with = _chat_with_module()
    capture(chat_with)
    capture(chat_common)

    chat_with.handle([], initialized_lore["context"])

    assert "Usage: chat_with" in buffer.getvalue()


def test_chat_with_enters_loop_and_exits_on_end_chat(
    initialized_lore, capture_rprint, monkeypatch
):
    capture, buffer = capture_rprint
    chat_with = _chat_with_module()
    capture(chat_with)
    capture(chat_common)

    monkeypatch.setattr(chat_common.chat_history, "get_or_create_session", lambda character: 1)
    monkeypatch.setattr(chat_common.chat_history, "get_history", lambda session_id, limit=4: [])
    monkeypatch.setattr(
        chat_with,
        "send_message_and_get_reply_safe",
        lambda character, message: f"Reply to: {message}",
    )

    prompts = iter(["Hello there", "end_chat"])
    monkeypatch.setattr(
        chat_with,
        "PromptSession",
        lambda: MagicMock(prompt=lambda *args, **kwargs: next(prompts)),
    )

    chat_with.handle(["Mara"], {"characters_in_lore": {"Mara"}})

    output = buffer.getvalue()
    assert "Chatting with Mara" in output
    assert "Mara>> Reply to: Hello there" in output
    assert "Ended chat with Mara" in output


def test_chat_with_supports_multi_word_character_names(
    initialized_lore, capture_rprint, monkeypatch
):
    capture, buffer = capture_rprint
    chat_with = _chat_with_module()
    capture(chat_with)
    capture(chat_common)

    captured = {}

    monkeypatch.setattr(
        chat_common.chat_history,
        "get_or_create_session",
        lambda character: captured.setdefault("character", character) or 1,
    )
    monkeypatch.setattr(chat_common.chat_history, "get_history", lambda session_id, limit=4: [])
    monkeypatch.setattr(
        chat_with,
        "send_message_and_get_reply_safe",
        lambda character, message: "Greetings.",
    )
    monkeypatch.setattr(
        chat_with,
        "PromptSession",
        lambda: MagicMock(prompt=lambda *args, **kwargs: "end_chat"),
    )

    chat_with.handle(
        ["The", "Mage", "of", "the", "Lake"],
        {"characters_in_lore": {"The Mage of the Lake"}},
    )

    assert captured["character"] == "The Mage of the Lake"


def test_chat_with_shows_recent_history(initialized_lore, capture_rprint, monkeypatch):
    capture, buffer = capture_rprint
    chat_with = _chat_with_module()
    capture(chat_with)
    capture(chat_common)

    monkeypatch.setattr(chat_common.chat_history, "get_or_create_session", lambda character: 1)
    monkeypatch.setattr(
        chat_common.chat_history,
        "get_history",
        lambda session_id, limit=4: [
            ("user", "Hello"),
            ("character", "Welcome back."),
        ],
    )
    monkeypatch.setattr(
        chat_with,
        "PromptSession",
        lambda: MagicMock(prompt=lambda *args, **kwargs: "end_chat"),
    )

    chat_with.handle(["Mara"], {"characters_in_lore": {"Mara"}})

    output = buffer.getvalue()
    assert "Recent conversation with Mara" in output
    assert "You>> Hello" in output
    assert "Mara>> Welcome back." in output


def test_chat_with_help_inside_loop(initialized_lore, capture_rprint, monkeypatch):
    capture, buffer = capture_rprint
    chat_with = _chat_with_module()
    capture(chat_with)
    capture(chat_common)

    monkeypatch.setattr(chat_common.chat_history, "get_or_create_session", lambda character: 1)
    monkeypatch.setattr(chat_common.chat_history, "get_history", lambda session_id, limit=4: [])
    prompts = iter(["help", "end_chat"])
    monkeypatch.setattr(
        chat_with,
        "PromptSession",
        lambda: MagicMock(prompt=lambda *args, **kwargs: next(prompts)),
    )

    chat_with.handle(["Mara"], {"characters_in_lore": {"Mara"}})

    assert "type end_chat" in buffer.getvalue().lower()

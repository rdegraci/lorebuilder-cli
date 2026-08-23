"""Tests for reset_chat command handler."""
import importlib

import commands.chat_common as chat_common
import lore


def _reset_chat_module():
    return importlib.import_module("commands.reset_chat")


def test_reset_chat_requires_character_name(initialized_lore, capture_rprint):
    capture, buffer = capture_rprint
    reset_chat = _reset_chat_module()
    capture(reset_chat)
    capture(chat_common)

    reset_chat.handle([], initialized_lore["context"])

    assert "Usage: reset_chat" in buffer.getvalue()


def test_reset_chat_clears_history(initialized_lore, capture_rprint, monkeypatch):
    capture, buffer = capture_rprint
    reset_chat = _reset_chat_module()
    capture(reset_chat)
    capture(chat_common)

    reset_called = {"value": False}

    monkeypatch.setattr(chat_common.chat_history, "get_or_create_session", lambda character: 7)

    def fake_reset(session_id):
        reset_called["value"] = True
        assert session_id == 7

    monkeypatch.setattr(chat_common.chat_history, "reset_history", fake_reset)

    reset_chat.handle(["Mara"], {"characters_in_lore": {"Mara"}})

    assert reset_called["value"] is True
    assert "Cleared chat history for Mara" in buffer.getvalue()


def test_reset_chat_rejects_unknown_character(initialized_lore, capture_rprint):
    capture, buffer = capture_rprint
    reset_chat = _reset_chat_module()
    capture(reset_chat)
    capture(chat_common)

    reset_chat.handle(["Unknown"], {"characters_in_lore": {"Mara"}})

    assert "not mentioned in any world lore" in buffer.getvalue()

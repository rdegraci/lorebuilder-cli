"""Tests for CLI command handlers."""
import importlib
from unittest.mock import MagicMock

import lore
from commands.add_lore import handle as add_lore_handle
from commands.list_characters import handle as list_characters_handle
from commands.store_generated_lore import handle as store_generated_lore_handle


def test_add_lore_command_updates_characters_in_lore(monkeypatch):
    add_lore_module = importlib.import_module("commands.add_lore")
    context = {
        "chroma_collection": MagicMock(),
        "characters_in_lore": set(),
    }
    context["chroma_collection"].get.return_value = {
        "documents": ["Mara lives in Ardelune."]
    }

    monkeypatch.setattr(add_lore_module.lore, "add_lore", lambda args, ctx: None)
    monkeypatch.setattr(
        add_lore_module,
        "extract_character_names_from_lore",
        lambda docs: {"Mara"},
    )

    add_lore_handle(["Mara lives in Ardelune."], context)

    assert context["characters_in_lore"] == {"Mara"}


def test_add_lore_command_warns_when_no_text_provided(capture_rprint, monkeypatch):
    capture, buffer = capture_rprint
    add_lore_module = importlib.import_module("commands.add_lore")

    capture(add_lore_module)
    monkeypatch.setattr("builtins.input", lambda prompt: "")

    add_lore_handle([], {})

    assert "No lore provided" in buffer.getvalue()


def test_store_generated_lore_command_updates_characters_in_lore(monkeypatch):
    store_module = importlib.import_module("commands.store_generated_lore")
    context = {
        "chroma_collection": MagicMock(),
        "characters_in_lore": set(),
        "last_generated_lore": "Mara founded Ardelune.",
    }
    context["chroma_collection"].get.return_value = {
        "documents": ["Mara founded Ardelune."]
    }

    monkeypatch.setattr(store_module.lore, "store_generated_lore", lambda args, ctx: None)
    monkeypatch.setattr(
        store_module,
        "extract_character_names_from_lore",
        lambda docs: {"Mara"},
    )

    store_generated_lore_handle([], context)

    assert context["characters_in_lore"] == {"Mara"}


def test_list_characters_command_prints_characters(capture_rprint):
    capture, buffer = capture_rprint
    list_characters_module = importlib.import_module("commands.list_characters")

    capture(list_characters_module)

    list_characters_handle([], {"characters_in_lore": {"Mara", "Arin"}})

    output = buffer.getvalue()
    assert "Characters mentioned in world lore" in output
    assert "Mara" in output
    assert "Arin" in output


def test_list_characters_command_handles_empty_set(capture_rprint):
    capture, buffer = capture_rprint
    list_characters_module = importlib.import_module("commands.list_characters")

    capture(list_characters_module)

    list_characters_handle([], {"characters_in_lore": set()})

    output = buffer.getvalue()
    assert "No characters found in lore" in output


def test_generate_lore_command_delegates_to_lore_module(initialized_lore, monkeypatch):
    called = {}

    def fake_generate_lore(args, context):
        called["args"] = args
        called["context"] = context

    monkeypatch.setattr(lore, "generate_lore", fake_generate_lore)

    generate_lore_module = importlib.import_module("commands.generate_lore")
    monkeypatch.setattr(generate_lore_module.lore, "generate_lore", fake_generate_lore)

    generate_lore_module.handle(["festival"], initialized_lore["context"])

    assert called["args"] == ["festival"]
    assert called["context"] is initialized_lore["context"]

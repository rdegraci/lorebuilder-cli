"""Tests for CLI dispatch loop."""
from unittest.mock import MagicMock

import cli
import cli_utils
import help as help_module
from commands import COMMANDS_REGISTRY


def _run_cli_with_inputs(monkeypatch, inputs, context=None):
    context = context or {"config": {}}
    prompts = iter(inputs)

    monkeypatch.setattr(cli, "print_banner", lambda: None)
    monkeypatch.setattr(cli, "print_command_menu", lambda registry=None: None)
    monkeypatch.setattr(cli, "cli_info", lambda msg: None)
    monkeypatch.setattr(
        cli,
        "PromptSession",
        lambda history: MagicMock(prompt=lambda *args, **kwargs: next(prompts)),
    )
    monkeypatch.setattr(cli, "FileHistory", lambda path: MagicMock())

    cli.start_cli(context)
    return context


def test_cli_exits_on_exit_command(monkeypatch):
    _run_cli_with_inputs(monkeypatch, ["exit"])


def test_cli_dispatches_registered_command(monkeypatch):
    called = {}

    def fake_handler(args, context):
        called["args"] = args
        called["context"] = context

    monkeypatch.setitem(COMMANDS_REGISTRY, "list_characters", fake_handler)

    context = _run_cli_with_inputs(monkeypatch, ["list_characters", "exit"])

    assert called["args"] == []
    assert called["context"] is context


def test_cli_strips_leading_slash_from_commands(monkeypatch):
    called = {}

    monkeypatch.setitem(
        COMMANDS_REGISTRY,
        "list_characters",
        lambda args, context: called.setdefault("ran", True),
    )

    _run_cli_with_inputs(monkeypatch, ["/list_characters", "exit"])

    assert called.get("ran") is True


def test_cli_help_without_args_shows_menu(monkeypatch, capture_rprint):
    capture, buffer = capture_rprint
    capture(cli)
    capture(help_module)
    monkeypatch.setattr(cli, "print_banner", lambda: None)
    monkeypatch.setattr(cli, "cli_info", lambda msg: None)
    monkeypatch.setattr(cli, "FileHistory", lambda path: MagicMock())

    prompts = iter(["help", "exit"])
    monkeypatch.setattr(
        cli,
        "PromptSession",
        lambda history: MagicMock(prompt=lambda *args, **kwargs: next(prompts)),
    )

    cli.start_cli({"config": {}})

    assert "Available Commands" in buffer.getvalue()


def test_cli_help_with_command_shows_details(monkeypatch, capture_rprint):
    capture, buffer = capture_rprint
    capture(cli)
    capture(help_module)
    monkeypatch.setattr(cli, "print_banner", lambda: None)
    monkeypatch.setattr(cli, "cli_info", lambda msg: None)
    monkeypatch.setattr(cli, "FileHistory", lambda path: MagicMock())

    prompts = iter(["help add_lore", "exit"])
    monkeypatch.setattr(
        cli,
        "PromptSession",
        lambda history: MagicMock(prompt=lambda *args, **kwargs: next(prompts)),
    )

    cli.start_cli({"config": {}})

    output = buffer.getvalue()
    assert "add_lore" in output
    assert "Usage:" in output


def test_cli_unknown_command_shows_error(monkeypatch, capture_rprint):
    capture, buffer = capture_rprint
    capture(cli)
    capture(cli_utils)
    monkeypatch.setattr(cli, "print_banner", lambda: None)
    monkeypatch.setattr(cli, "print_command_menu", lambda registry=None: None)
    monkeypatch.setattr(cli, "cli_info", lambda msg: None)
    monkeypatch.setattr(cli, "FileHistory", lambda path: MagicMock())

    prompts = iter(["not_a_real_command", "exit"])
    monkeypatch.setattr(
        cli,
        "PromptSession",
        lambda history: MagicMock(prompt=lambda *args, **kwargs: next(prompts)),
    )

    cli.start_cli({"config": {}})

    assert "Unknown command" in buffer.getvalue()


def test_cli_passes_command_arguments_to_handler(monkeypatch):
    called = {}

    monkeypatch.setitem(
        COMMANDS_REGISTRY,
        "query_lore",
        lambda args, context: called.setdefault("args", args),
    )

    _run_cli_with_inputs(monkeypatch, ["query_lore council secrets", "exit"])

    assert called["args"] == ["council", "secrets"]

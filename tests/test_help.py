"""Tests for CLI help output."""
import help as help_module
from commands import COMMANDS_REGISTRY


def test_print_command_help_shows_usage_and_examples(capture_rprint):
    capture, buffer = capture_rprint
    capture(help_module)

    help_module.print_command_help("add_lore", COMMANDS_REGISTRY)
    output = buffer.getvalue()

    assert "add_lore" in output
    assert "Usage:" in output
    assert "Examples:" in output
    assert "add_lore The city of Ardelune" in output


def test_print_command_help_for_generate_lore_mentions_store(capture_rprint):
    capture, buffer = capture_rprint
    capture(help_module)

    help_module.print_command_help("generate_lore", COMMANDS_REGISTRY)
    output = buffer.getvalue()

    assert "store_generated_lore" in output
    assert "not saved to the world" in output


def test_print_command_help_unknown_command(capture_rprint):
    capture, buffer = capture_rprint
    capture(help_module)

    help_module.print_command_help("not_a_command", COMMANDS_REGISTRY)
    output = buffer.getvalue()

    assert "No such command" in output


def test_print_command_menu_lists_registered_commands(capture_rprint):
    capture, buffer = capture_rprint
    capture(help_module)

    help_module.print_command_menu(COMMANDS_REGISTRY)
    output = buffer.getvalue()

    assert "Available Commands" in output
    assert "add_lore" in output
    assert "chat_to" in output
    assert "chat_with" in output
    assert "help <command>" in output

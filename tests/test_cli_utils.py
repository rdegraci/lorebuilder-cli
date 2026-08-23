"""Tests for CLI output helpers."""
import cli_utils


def test_print_usage_shows_literal_angle_brackets(capture_rprint):
    capture, buffer = capture_rprint
    capture(cli_utils)

    cli_utils.print_usage("add_lore <lore_text>", style="yellow")
    output = buffer.getvalue()

    assert "Usage: add_lore <lore_text>" in output


def test_print_literal_shows_square_brackets(capture_rprint):
    capture, buffer = capture_rprint
    capture(cli_utils)

    cli_utils.print_literal("help [command]", style="white", prefix="  ")
    output = buffer.getvalue()

    assert "help [command]" in output

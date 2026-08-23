"""
cli_utils.py - Consistent CLI output helpers for LoreBuilder.
"""
from typing import Optional

from rich import print as rprint
from rich.text import Text


def print_literal(text: str, style: Optional[str] = None, *, prefix: str = "") -> None:
    """Print text without interpreting Rich markup in the string."""
    rprint(Text(prefix + text, style=style))


def print_usage(
    usage: str,
    *,
    prefix: str = "Usage:",
    style: str = "cyan",
    leading_newline: bool = False,
) -> None:
    """Print a usage line; angle brackets and square brackets are shown literally."""
    parts = []
    if leading_newline:
        parts.append(("\n", None))
    parts.extend([(f"{prefix} ", style), (usage, None)])
    rprint(Text.assemble(*parts))


def cli_error(msg: str):
    """Display an error message (red, with [ERROR] prefix)."""
    rprint(f"[bold red][ERROR][/bold red] {msg}")

def cli_warn(msg: str):
    """Display a warning message (yellow, with [WARNING] prefix)."""
    rprint(f"[bold yellow][WARNING][/bold yellow] {msg}")

def cli_info(msg: str):
    """Display informational message (cyan)."""
    rprint(f"[cyan]{msg}")

def cli_success(msg: str):
    """Display a success message (green, with checkmark)."""
    rprint(f"[bold green]✔[/bold green] {msg}")

def cli_debug(msg: str, verbose: bool = False):
    """Display a debug message (grey/dim), if verbosity is set."""
    if verbose:
        rprint(f"[dim]{msg}[/dim]")

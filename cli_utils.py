"""
cli_utils.py - Consistent CLI output helpers for LoreBuilder.
"""
from rich import print as rprint

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

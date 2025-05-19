"""
help.py - Banner and command/help menu utilities for CLI
"""
from rich import print as rprint

BANNER = (
    "[bold cyan]╔═════════════════════════════════════════════════════════╗\n"
    "║            LoreBuilder CLI - World Builder              ║\n"
    "╚═════════════════════════════════════════════════════════╝[/bold cyan]"
)

LORE_COMMANDS = [
    "add_lore", "generate_lore", "store_generated_lore", "query_lore", "list_all_lore", "delete_lore"
]
NAV_COMMANDS = [
    "look", "save_look", "go", "reset_location", "history"
]
CHAR_COMMANDS = [
    "chat_as", "reset"
]
SYSTEM_COMMANDS = ["help", "exit"]

def print_banner():
    """
    Prints the application banner/logo.
    """
    rprint(BANNER)

def print_command_menu(commands_registry=None):
    """
    Prints out the available commands by category.
    Descriptions are sourced from command docstrings if present.
    """
    rprint("[bold cyan]Available Commands:[/bold cyan]")
    rprint("[cyan]Lore: [white]add_lore, generate_lore, store_generated_lore, query_lore, list_all_lore, delete_lore")
    rprint("[cyan]Navigation: [white]look, save_look, go <direction>, reset_location, history")
    rprint("[cyan]Characters: [white]chat_as <character> <message>, reset <character>")
    rprint("[cyan]System: [white]help, exit")
    if commands_registry:
        rprint("\n[dim]Type 'help <command>' for usage if available.[/dim]")

def print_command_help(command, commands_registry):
    """
    Prints detailed help for a single command, if available.
    """
    handler = commands_registry.get(command)
    if not handler:
        rprint(f"[red]No such command: {command}")
        return
    doc = handler.__doc__
    if doc:
        rprint(f"[cyan]Help for '[bold]{command}[/bold]':\n{doc.strip()}")
    else:
        rprint(f"[grey]No help available for command: {command}")

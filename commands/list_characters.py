"""
commands/list_characters.py

Handles the list_characters CLI command for LoreBuilder.
Displays all character/person names extracted from lore via spaCy NER.
"""
from rich import print as rprint

def handle(args, context):
    """
    Handles the list_characters CLI command.
    Args:
        args (list): Command arguments (ignored)
        context (dict): Shared context dictionary containing 'characters_in_lore'.
    """
    characters = context.get('characters_in_lore', set())
    if not characters:
        rprint("[dim]No characters found in lore. Add more lore first![/dim]")
        return
    rprint(f"[cyan]Characters mentioned in world lore ([bold]{len(characters)}[/bold]):")
    for c in sorted(characters):
        rprint(f"- [bold]{c}[/bold]")
    rprint("[dim]Use chat_to for a quick message or chat_with for a conversation.[/dim]")

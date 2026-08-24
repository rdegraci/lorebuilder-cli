"""
commands/list_characters.py

Handles the list_characters CLI command for LoreBuilder.
Displays all character/person names extracted from lore via spaCy NER.
"""
from rich import print as rprint

import character_aliases


def handle(args, context):
    """
    Handles the list_characters CLI command.
    Args:
        args (list): Command arguments (ignored)
        context (dict): Shared context dictionary containing 'characters_in_lore'.
    """
    characters = set(context.get("characters_in_lore", []))
    aliases = character_aliases.get_all()

    if not characters:
        rprint("[dim]No characters found in lore. Add more lore first![/dim]")
        return

    effective = character_aliases.build_effective_characters(characters, aliases)
    rprint(f"[cyan]Characters mentioned in world lore ([bold]{len(effective)}[/bold]):")
    for display_name in sorted(effective):
        lore_names = [
            lore_name
            for lore_name in characters
            if aliases.get(lore_name, lore_name) == display_name
        ]
        if len(lore_names) == 1 and lore_names[0] != display_name:
            rprint(f"- [bold]{display_name}[/bold] [dim](lore: {lore_names[0]})[/dim]")
        else:
            rprint(f"- [bold]{display_name}[/bold]")
    rprint(
        "[dim]Use chat_to for a quick message, chat_with for a conversation, "
        "rename_character to change a display name, or reset_chat to clear history.[/dim]"
    )

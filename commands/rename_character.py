
"""
commands/rename_character.py

Handles the rename_character CLI command to assign a display/chat alias
for a character name extracted from lore.
"""
from rich import print as rprint

import character_aliases
import chat_history
from cli_utils import print_usage

from .chat_common import (
    check_lore_service,
    parse_two_character_names,
)


def handle(args, context):
    """
    Handles the rename_character <old_name> <new_name> CLI command.

    Maps a lore-extracted name to a preferred display name for chat and listing.
    Lore text is unchanged; chat queries use both names for context.
    """
    if not check_lore_service("rename_character"):
        return

    old_name, new_name, parse_warning = parse_two_character_names(args)
    if parse_warning:
        rprint(parse_warning)
    if not old_name or not new_name:
        print_usage("rename_character <old_name> <new_name>", style="red")
        return

    if old_name.strip().lower() == new_name.strip().lower():
        rprint("[yellow]Old and new names are the same; nothing to change.")
        return

    characters_in_lore = set(context.get("characters_in_lore", []))
    aliases = character_aliases.get_all()

    lore_name = character_aliases.find_lore_name(old_name, characters_in_lore, aliases)
    if not lore_name:
        rprint(f"[red]Character '{old_name}' is not mentioned in any world lore.")
        rprint("Use 'list_characters' to see known characters.")
        return

    current_display = aliases.get(lore_name, lore_name)
    if (
        new_name in characters_in_lore
        and new_name != lore_name
        and character_aliases.get_display_name(new_name, aliases) == new_name
    ):
        rprint(
            f"[red]Cannot rename to '{new_name}': that name already refers to a different "
            "character in lore."
        )
        return

    character_aliases.set_alias(lore_name, new_name)

    for session_name in dict.fromkeys([lore_name, current_display]):
        chat_history.rename_session_character(session_name, new_name)

    if lore_name != new_name:
        rprint(
            f"[green]Renamed {lore_name} → {new_name} for chat. "
            "Lore text is unchanged; both names are used for context."
        )
    else:
        rprint(f"[green]Character chat name set to {new_name}.")

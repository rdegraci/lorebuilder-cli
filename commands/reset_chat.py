
"""
commands/reset_chat.py

Handles the reset_chat CLI command to clear a character's conversation history.
"""
from rich import print as rprint

import chat_history
from .chat_common import check_lore_service, parse_character_from_args, resolve_character


def handle(args, context):
    """
    Handles the reset_chat <character> CLI command.

    Clears all messages for a character's chat session while keeping the session.
    """
    if not check_lore_service("reset_chat"):
        return

    character_name, parse_warning = parse_character_from_args(args)
    if parse_warning:
        rprint(parse_warning)
    if not character_name:
        rprint("[red]Usage: reset_chat <character_name>")
        return

    character_to_use = resolve_character(
        character_name,
        context.get("characters_in_lore", []),
    )
    if not character_to_use:
        return

    session_id = chat_history.get_or_create_session(character_to_use)
    chat_history.reset_history(session_id)
    rprint(f"[green]Cleared chat history for {character_to_use}.")

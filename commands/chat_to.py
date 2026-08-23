
"""
commands/chat_to.py

Handles the chat_to CLI command for LoreBuilder.
"""
from rich import print as rprint

from .chat_common import (
    check_lore_service,
    parse_character_and_message,
    print_character_reply,
    resolve_character,
    send_message_and_get_reply_safe,
)


def handle(args, context):
    """
    Handles the chat_to <character> <message> CLI command.
    """
    if not check_lore_service("chat_to"):
        return

    character_name, user_message, parse_error = parse_character_and_message(args)
    if parse_error:
        rprint(parse_error)
    if not character_name or not user_message:
        rprint("[red]Usage: chat_to <character_name> <user_message>")
        return

    character_to_use = resolve_character(
        character_name,
        context.get("characters_in_lore", []),
    )
    if not character_to_use:
        return

    reply = send_message_and_get_reply_safe(character_to_use, user_message)
    if reply is not None:
        print_character_reply(character_to_use, reply)

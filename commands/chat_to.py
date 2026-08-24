
"""
commands/chat_to.py

Handles the chat_to CLI command for LoreBuilder.
"""
from rich import print as rprint

from cli_utils import print_usage

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
        print_usage("chat_to <character_name> <user_message>", style="red")
        return

    character_to_use = resolve_character(
        character_name,
        context.get("characters_in_lore", []),
    )
    if not character_to_use:
        return

    lore_characters = set(context.get("characters_in_lore", []))
    reply = send_message_and_get_reply_safe(
        character_to_use,
        user_message,
        characters_in_lore=lore_characters,
    )
    if reply is not None:
        print_character_reply(character_to_use, reply)

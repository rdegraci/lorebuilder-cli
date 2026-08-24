
"""
commands/chat_with.py

Handles the chat_with CLI command for multi-turn character conversations.
"""
from rich import print as rprint
from prompt_toolkit import PromptSession

from cli_utils import print_usage

from .chat_common import (
    check_lore_service,
    generate_opening_greeting_safe,
    parse_character_from_args,
    print_character_reply,
    print_recent_history,
    resolve_character,
    send_message_and_get_reply_safe,
)

import chat_history

END_CHAT_COMMANDS = {"end_chat", "/end_chat", "done", "leave"}


def handle(args, context):
    """
    Handles the chat_with <character> CLI command.

    Enters a conversation loop with the character until the user types end_chat.
    Character replies use Character>> and user input uses You>>.
    """
    if not check_lore_service("chat_with"):
        return

    character_name, parse_warning = parse_character_from_args(args)
    if parse_warning:
        rprint(parse_warning)
    if not character_name:
        print_usage("chat_with <character_name>", style="red")
        return

    character_to_use = resolve_character(
        character_name,
        context.get("characters_in_lore", []),
    )
    if not character_to_use:
        return

    session_id = chat_history.get_or_create_session(character_to_use)
    rprint(
        f"Chatting with {character_to_use}. "
        "Type end_chat to return to the main menu."
    )

    lore_characters = set(context.get("characters_in_lore", []))
    history = chat_history.get_history(session_id, limit=1)
    if history:
        print_recent_history(character_to_use, session_id)
    else:
        greeting = generate_opening_greeting_safe(
            character_to_use,
            characters_in_lore=lore_characters,
        )
        if greeting is not None:
            print_character_reply(character_to_use, greeting)

    session = PromptSession()
    while True:
        try:
            user_message = session.prompt("You>> ").strip()
        except (EOFError, KeyboardInterrupt):
            rprint(f"\nEnded chat with {character_to_use}.")
            break

        if not user_message:
            continue

        if user_message.lower() in END_CHAT_COMMANDS:
            rprint(f"Ended chat with {character_to_use}.")
            break

        if user_message.lower() == "help":
            rprint(
                "Continue the conversation, or type end_chat to return to the main menu."
            )
            continue

        reply = send_message_and_get_reply_safe(
            character_to_use,
            user_message,
            characters_in_lore=lore_characters,
        )
        if reply is not None:
            print_character_reply(character_to_use, reply)

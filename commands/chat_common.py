"""
commands/chat_common.py

Shared character chat logic for chat_to and chat_with commands.
"""
import traceback
from typing import List, Optional, Set, Tuple

import litellm
from rich import print as rprint

import chat_history
import lore
from llm_utils import extract_completion_text
from lore_fuzzy import find_best_character_match


def check_lore_service(command_name: str) -> bool:
    """Return True if the lore service is initialized."""
    if getattr(lore, "_lore_service", None) is None:
        rprint(f"[red]Error: Lore service is not initialized! Cannot proceed with {command_name}.")
        return False
    return True


def parse_character_from_args(args: List[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse a character name from CLI args, supporting quoted multi-word names.
    All tokens are treated as the character name when unquoted.

    Returns:
        (character_name, warning_message)
    """
    if not args:
        return None, None

    first_arg = args[0]
    if first_arg.startswith('"') or first_arg.startswith("'"):
        opening_quote = first_arg[0]
        char_name_parts = []
        part = first_arg[1:]
        if part:
            char_name_parts.append(part)

        for i in range(1, len(args)):
            if args[i].endswith(opening_quote):
                if len(args[i]) > 1:
                    char_name_parts.append(args[i][:-1])
                return " ".join(char_name_parts).strip(), None
            char_name_parts.append(args[i])

        char_name = " ".join(char_name_parts).strip()
        return char_name, "[yellow]Warning: No closing quote found for character name."

    return " ".join(args).strip(), None


def parse_character_and_message(args: List[str]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Parse character name and message for chat_to.

    Returns:
        (character_name, user_message, error_or_warning)
    """
    if not args or len(args) < 2:
        return None, None, "[red]Usage: chat_to <character_name> <user_message>"

    first_arg = args[0]
    if first_arg.startswith('"') or first_arg.startswith("'"):
        opening_quote = first_arg[0]
        char_name_parts = []
        part = first_arg[1:]
        if part:
            char_name_parts.append(part)

        for i in range(1, len(args)):
            if args[i].endswith(opening_quote):
                if len(args[i]) > 1:
                    char_name_parts.append(args[i][:-1])
                char_name = " ".join(char_name_parts).strip()
                user_message = " ".join(args[i + 1 :]).strip()
                return char_name, user_message, None
            char_name_parts.append(args[i])

        char_name = " ".join(char_name_parts).strip()
        return char_name, "", "[yellow]Warning: No closing quote found for character name."

    character_name = first_arg.strip()
    user_message = " ".join(args[1:]).strip()
    return character_name, user_message, None


def resolve_character(
    character_name: str,
    characters_in_lore: Set[str],
) -> Optional[str]:
    """
    Fuzzy-match a character name against lore characters.

    Returns the resolved character name, or None after printing errors.
    """
    best_match, close_matches = find_best_character_match(character_name, characters_in_lore)

    if not best_match:
        rprint(f"[red]Character '{character_name}' is not mentioned in any world lore.")
        if close_matches:
            suggestions = ", ".join(close_matches)
            rprint(f"[yellow]Did you mean: {suggestions}?")
        rprint("Use 'list_characters' to see known characters.")
        return None

    if best_match.strip().lower() != character_name.strip().lower():
        rprint(f"[yellow]Interpreting '{character_name}' as '{best_match}' for this session.")

    return best_match


def format_character_line(character_name: str, message: str) -> str:
    """Format a character reply for display."""
    return f"[bold magenta]{character_name}>>[/bold magenta] {message}"


def print_character_reply(character_name: str, message: str) -> None:
    """Print a character reply using the standard transcript format."""
    rprint(format_character_line(character_name, message))


def print_recent_history(character_name: str, session_id: int, limit: int = 4) -> None:
    """Show recent conversation history when entering a chat session."""
    history = chat_history.get_history(session_id, limit=limit)
    if not history:
        return

    rprint(f"Recent conversation with {character_name}:")
    for role, message in history:
        if role == "user":
            rprint(f"You>> {message}")
        else:
            rprint(format_character_line(character_name, message))
    rprint("")


def send_message_and_get_reply(character_name: str, user_message: str) -> str:
    """
    Store the user message, call the LLM, store the reply, and return reply text.
    """
    session_id = chat_history.get_or_create_session(character_name)
    chat_history.add_message(session_id, "user", user_message)

    relevant_lore = lore.query_lore_internal(f"{character_name} {user_message}", 3)
    messages = chat_history.get_history(session_id)
    context_str = (
        "\n\n".join(relevant_lore)
        if relevant_lore
        else "No specific lore found for this character."
    )

    llm_messages = [
        {
            "role": "system",
            "content": lore._lore_service.config.get("chat_prompt_template", "")
            .replace("{character_name}", character_name)
            .replace("{context}", context_str),
        }
    ]

    for role, msg in messages:
        llm_messages.append(
            {"role": "user" if role == "user" else "assistant", "content": msg}
        )

    response = litellm.completion(
        model=lore._lore_service.config.get("llm_provider", "openai/gpt-4o-mini"),
        messages=llm_messages,
        api_key=lore._lore_service.llm_api_key,
        max_tokens=512,
    )

    reply = extract_completion_text(response)
    chat_history.add_message(session_id, "character", reply)
    return reply


def send_message_and_get_reply_safe(character_name: str, user_message: str) -> Optional[str]:
    """Call send_message_and_get_reply and print errors instead of raising."""
    try:
        return send_message_and_get_reply(character_name, user_message)
    except Exception as e:
        traceback.print_exc()
        rprint(f"[red]Error during LLM chat: {str(e)}")
        return None

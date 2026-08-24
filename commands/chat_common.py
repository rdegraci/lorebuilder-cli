"""
commands/chat_common.py

Shared character chat logic for chat_to and chat_with commands.
"""
import traceback
from typing import List, Optional, Set, Tuple

import litellm
from rich import print as rprint

import chat_history
import character_aliases
import lore
from llm_utils import extract_completion_text


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


def _take_character_name(args: List[str]) -> Tuple[Optional[str], List[str]]:
    """Parse one character name from the front of args and return the remainder."""
    if not args:
        return None, []

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
                return " ".join(char_name_parts).strip(), args[i + 1 :]
            char_name_parts.append(args[i])

        return " ".join(char_name_parts).strip(), []

    return first_arg.strip(), args[1:]


def parse_two_character_names(args: List[str]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Parse two character names from CLI args for rename_character.

    Returns:
        (old_name, new_name, warning_message)
    """
    if len(args) < 2:
        return None, None, None

    args = list(args)
    if args[0].startswith('"') or args[0].startswith("'"):
        old_name, remainder = _take_character_name(args)
        if not old_name or not remainder:
            return None, None, None

        new_name, extra = _take_character_name(remainder)
        if not new_name:
            return None, None, None

        warning = "[yellow]Warning: Extra arguments ignored." if extra else None
        return old_name, new_name, warning

    if len(args) == 2:
        return args[0].strip(), args[1].strip(), None

    return " ".join(args[:-1]).strip(), args[-1].strip(), None


def parse_character_and_message(args: List[str]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Parse character name and message for chat_to.

    Returns:
        (character_name, user_message, error_or_warning)
    """
    if not args or len(args) < 2:
        return None, None, None

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


def build_lore_query(
    display_name: str,
    extra: str,
    characters_in_lore: Set[str],
) -> str:
    """Build a lore search query using display and underlying lore names."""
    aliases = character_aliases.get_all()
    terms = character_aliases.lore_search_terms(display_name, characters_in_lore, aliases)
    parts = terms + ([extra] if extra else [])
    return " ".join(part for part in parts if part)


def resolve_character(
    character_name: str,
    characters_in_lore: Set[str],
) -> Optional[str]:
    """
    Fuzzy-match a character name against lore characters and aliases.

    Returns the resolved display/chat name, or None after printing errors.
    """
    aliases = character_aliases.get_all()
    lore_characters = set(characters_in_lore)
    display_name, close_matches = character_aliases.resolve_display_name(
        character_name,
        lore_characters,
        aliases,
    )

    if not display_name:
        rprint(f"[red]Character '{character_name}' is not mentioned in any world lore.")
        if close_matches:
            suggestions = ", ".join(close_matches)
            rprint(f"[yellow]Did you mean: {suggestions}?")
        rprint("Use 'list_characters' to see known characters.")
        return None

    if display_name.strip().lower() != character_name.strip().lower():
        rprint(f"[yellow]Interpreting '{character_name}' as '{display_name}' for this session.")

    return display_name


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


def send_message_and_get_reply(
    character_name: str,
    user_message: str,
    characters_in_lore: Optional[Set[str]] = None,
) -> str:
    """
    Store the user message, call the LLM, store the reply, and return reply text.
    """
    session_id = chat_history.get_or_create_session(character_name)
    chat_history.add_message(session_id, "user", user_message)

    lore_chars = set(characters_in_lore or [])
    lore_query = build_lore_query(character_name, user_message, lore_chars)
    relevant_lore = lore.query_lore_internal(lore_query, 3)
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


def send_message_and_get_reply_safe(
    character_name: str,
    user_message: str,
    characters_in_lore: Optional[Set[str]] = None,
) -> Optional[str]:
    """Call send_message_and_get_reply and print errors instead of raising."""
    try:
        return send_message_and_get_reply(
            character_name,
            user_message,
            characters_in_lore=characters_in_lore,
        )
    except Exception as e:
        traceback.print_exc()
        rprint(f"[red]Error during LLM chat: {str(e)}")
        return None


def generate_opening_greeting(
    character_name: str,
    characters_in_lore: Optional[Set[str]] = None,
) -> Optional[str]:
    """
    Generate an in-character greeting when starting a new conversation.

    Returns None if the character already has message history.
    """
    session_id = chat_history.get_or_create_session(character_name)
    if chat_history.get_history(session_id, limit=1):
        return None

    lore_chars = set(characters_in_lore or [])
    lore_query = build_lore_query(character_name, "", lore_chars)
    relevant_lore = lore.query_lore_internal(lore_query, 3)
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
        },
        {
            "role": "user",
            "content": (
                "The user has just entered to speak with you. "
                "Greet them briefly in character and invite them to talk."
            ),
        },
    ]

    response = litellm.completion(
        model=lore._lore_service.config.get("llm_provider", "openai/gpt-4o-mini"),
        messages=llm_messages,
        api_key=lore._lore_service.llm_api_key,
        max_tokens=512,
    )

    reply = extract_completion_text(response)
    chat_history.add_message(session_id, "character", reply)
    return reply


def generate_opening_greeting_safe(
    character_name: str,
    characters_in_lore: Optional[Set[str]] = None,
) -> Optional[str]:
    """Call generate_opening_greeting and print errors instead of raising."""
    try:
        return generate_opening_greeting(
            character_name,
            characters_in_lore=characters_in_lore,
        )
    except Exception as e:
        traceback.print_exc()
        rprint(f"[red]Error generating greeting: {str(e)}")
        return None

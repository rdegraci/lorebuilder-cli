
"""
commands/chat_as.py

Handles the chat_as CLI command for LoreBuilder after refactoring.
"""
import traceback
from rich import print as rprint
import litellm
import lore
import chat_history
from lore_fuzzy import find_best_character_match
from llm_utils import extract_completion_text

def handle(args, context):
    """
    Handles the chat_as <character> <message> CLI command.

    Attempts fuzzy matching of the provided character_name against context['characters_in_lore'],
    using case-insensitive match, basic name variations, and similarity scoring.
    If a close match is found, informs the user and interprets input as that character.
    If not found, prints an error and suggests possible alternatives.

    Args:
        args (list): Command arguments
        context (dict): Shared context dictionary
    """

    # --- Helper: Improved argument parser allowing for quoted names ---
    def parse_character_and_message(args):
        """
        Returns a tuple: (character_name (str), user_message (str), error (str or None))
        Handles smart parsing for quoted multi-word character names with both single/double quotes.
        """
        if not args or len(args) < 2:
            return None, None, "[red]Usage: chat_as <character_name> <user_message>"

        first_arg = args[0]
        if (first_arg.startswith('"') or first_arg.startswith("'")):
            opening_quote = first_arg[0]
            char_name_parts = []
            close_found = False
            # Remove opening quote
            part = first_arg[1:]
            if part:
                char_name_parts.append(part)
            # search for closing quote in subsequent args
            for i in range(1, len(args)):
                if args[i].endswith(opening_quote):
                    # closing quote found
                    if len(args[i]) > 1:
                        char_name_parts.append(args[i][:-1])
                    close_found = True
                    char_name = ' '.join(char_name_parts).strip()
                    user_message = ' '.join(args[i+1:]).strip()
                    return char_name, user_message, None
                char_name_parts.append(args[i])
            # No closing quote found; fallback: treat everything as character name
            char_name = ' '.join(char_name_parts).strip()
            user_message = ''
            return char_name, user_message, "[yellow]Warning: No closing quote found for character name."
        else:
            # Not quoted: treat first arg as character_name
            character_name = first_arg.strip()
            user_message = ' '.join(args[1:]).strip()
            return character_name, user_message, None

    # --- SAFETY CHECK for lore._lore_service ---
    if getattr(lore, "_lore_service", None) is None:
        rprint("[red]Error: Lore service is not initialized! Cannot proceed with chat_as.")
        return

    character_name, user_message, parse_error = parse_character_and_message(args)
    if parse_error:
        rprint(parse_error)
    if not character_name or not user_message:
        rprint("[red]Usage: chat_as <character_name> <user_message>")
        return

    # --- Character presence check for lore world with fuzzy matching ---
    characters_in_lore = context.get('characters_in_lore', [])

    # Fuzzy match character name
    best_match, close_matches = find_best_character_match(character_name, characters_in_lore)

    if not best_match:
        rprint(f"[red]Character '{character_name}' is not mentioned in any world lore.")
        if close_matches:
            suggestions = ', '.join(close_matches)
            rprint(f"[yellow]Did you mean: {suggestions}?")
        rprint("Use 'list_characters' to see known characters.")
        return

    # If user input doesn't match best_match (case-insensitive), warn about selection
    if best_match.strip().lower() != character_name.strip().lower():
        rprint(f"[yellow]Interpreting '{character_name}' as '{best_match}' for this session.")

    character_to_use = best_match

    try:
        # Get character session
        session_id = chat_history.get_or_create_session(character_to_use)

        # Store user message
        chat_history.add_message(session_id, "user", user_message)

        # Get relevant lore for context
        relevant_lore = lore.query_lore_internal(f"{character_to_use} {user_message}", 3)

        # Get conversation history
        messages = chat_history.get_history(session_id)

        # Format context
        context_str = "\n\n".join(relevant_lore) if relevant_lore else "No specific lore found for this character."

        # Prepare messages for LLM
        llm_messages = [
            {
                "role": "system",
                "content": lore._lore_service.config.get("chat_prompt_template", "").replace("{character_name}", character_to_use).replace("{context}", context_str)
            }
        ]

        # Add conversation history
        for role, msg in messages:
            llm_messages.append({"role": "user" if role == "user" else "assistant", "content": msg})

        # Make LLM request
        response = litellm.completion(
            model=lore._lore_service.config.get("llm_provider", "openai/gpt-4o-mini"),
            messages=llm_messages,
            api_key=lore._lore_service.llm_api_key,
            max_tokens=512
        )

        reply = extract_completion_text(response)

        # Store character response
        chat_history.add_message(session_id, "character", reply)

        # Display to user
        rprint(f"[bold magenta]{character_to_use}:[/bold magenta] {reply}")

    except Exception as e:
        traceback.print_exc()
        rprint(f"[red]Error during LLM chat: {str(e)}")



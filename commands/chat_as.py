"""
commands/chat_as.py

Handles the chat_as CLI command for LoreBuilder after refactoring.
"""
import traceback
from rich import print as rprint
import litellm
import lore
import chat_history

def handle(args, context):
    """
    Handles the chat_as <character> <message> CLI command.
    
    Args:
        args (list): Command arguments
        context (dict): Shared context dictionary
    """
    if not args or len(args) < 2:
        rprint("[red]Usage: chat_as <character_name> <user_message>")
        return
        
    character_name = args[0].strip()
    user_message = ' '.join(args[1:]).strip()
    
    if not character_name or not user_message:
        rprint("[red]Usage: chat_as <character_name> <user_message>")
        return
        
    try:
        # Get character session
        session_id = chat_history.get_or_create_session(character_name)
        
        # Store user message
        chat_history.add_message(session_id, "user", user_message)
        
        # Get relevant lore for context
        relevant_lore = lore.query_lore_internal(f"{character_name} {user_message}", 3)
        
        # Get conversation history
        messages = chat_history.get_history(session_id)
        
        # Format context
        context_str = "\n\n".join(relevant_lore) if relevant_lore else "No specific lore found for this character."
        
        # Prepare messages for LLM
        llm_messages = [
            {"role": "system", "content": lore._config.get("chat_prompt_template", "").replace("{character_name}", character_name).replace("{context}", context_str)}
        ]
        
        # Add conversation history
        for role, msg in messages:
            llm_messages.append({"role": "user" if role == "user" else "assistant", "content": msg})
            
        # Make LLM request
        response = litellm.completion(
            model=lore._config.get("llm_provider", "openai/gpt-4o-mini"),
            messages=llm_messages,
            api_key=lore._llm_api_key,
            max_tokens=512
        )
        
        reply = response["choices"][0]["message"]["content"]
        
        # Store character response
        chat_history.add_message(session_id, "character", reply)
        
        # Display to user
        rprint(f"[bold magenta]{character_name}:[/bold magenta] {reply}")
        
    except Exception as e:
        traceback.print_exc()
        rprint(f"[red]Error during LLM chat: {str(e)}")
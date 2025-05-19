"""
commands/reset.py

Handles the /reset CLI command for LoreBuilder after refactoring.
"""
from chat_history import get_or_create_session, reset_history
from rich import print as rprint

def handle(args, context):
    """
    Handles the /reset <character> CLI command.
    
    Args:
        args (list): Command arguments
        context (dict): Shared context dictionary
    """
    if not args:
        rprint("[red]Usage: /reset <character>")
        return
        
    char_name = ' '.join(args).strip()
    
    # Get session ID for character
    session_id = get_or_create_session(char_name)
    
    # Reset chat history
    reset_history(session_id)
    
    rprint(f"[cyan]History for character '{char_name}' reset.")
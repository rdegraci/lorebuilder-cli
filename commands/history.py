"""
commands/history.py

Handles the /history CLI command for LoreBuilder after refactoring.
"""
from chat_history import get_or_create_session, get_history
from rich import print as rprint

def handle(args, context):
    """
    Handles the /history <character> CLI command.
    
    Args:
        args (list): Command arguments
        context (dict): Shared context dictionary
    """
    if not args:
        rprint("[red]Usage: /history <character>")
        return
        
    char_name = ' '.join(args).strip()
    
    # Get session ID for character
    session_id = get_or_create_session(char_name)
    
    # Get history for session
    hist = get_history(session_id, limit=40)
    
    if not hist:
        rprint(f"[dim]No history for '{char_name}'.")
    else:
        rprint(f"[bold cyan]Chat history for '{char_name}':[/bold cyan]")
        for i, (role, msg) in enumerate(hist, 1):
            who = "[green]You[/green]" if role == 'user' else f"[magenta]{char_name}[/magenta]"
            rprint(f"{who}: {msg}")
"""
commands/save_look.py

Handles the /save_look CLI command for LoreBuilder after refactoring.
"""
from locations import save_look as save_look_func
from rich import print as rprint

def handle(args, context):
    """
    Handles the /save_look CLI command.
    
    Args:
        args (list): Command arguments
        context (dict): Shared context dictionary
    """
    # If args are provided, use the first as character name, otherwise prompt
    if args:
        character_name = args[0]
    else:
        character_name = input("Character/session for /save_look: ").strip()
        
    if not character_name:
        rprint("[red]You must enter a character/session name.")
        return
        
    # Pass args to the save_look function from locations module
    save_look_func([character_name], context)
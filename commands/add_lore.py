"""
commands/add_lore.py

Handles the add_lore CLI command for LoreBuilder after refactoring.
"""
import lore
from rich import print as rprint

def handle(args, context):
    """
    Handles the add_lore CLI command.
    
    Args:
        args (list): Command arguments
        context (dict): Shared context dictionary
    """
    # If args are provided, join them as the lore text, otherwise prompt
    lore_text = ' '.join(args).strip() if args else input("Paste lore to add: ")
    
    if not lore_text:
        rprint("[red]No lore provided.")
        return
        
    # Call the lore module's add_lore function
    lore.add_lore([lore_text], context)
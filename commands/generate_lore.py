"""
commands/generate_lore.py

Handles the generate_lore CLI command for LoreBuilder after refactoring.
"""
import lore
from rich import print as rprint

def handle(args, context):
    """
    Handles the generate_lore CLI command.
    
    Args:
        args (list): Command arguments
        context (dict): Shared context dictionary
    """
    # If args are provided, join them as the topic, otherwise prompt
    topic = ' '.join(args).strip() if args else input("Topic or query: ")
    
    if not topic:
        rprint("[red]No topic provided.")
        return
        
    # Call the lore module's generate_lore function
    lore.generate_lore([topic], context)
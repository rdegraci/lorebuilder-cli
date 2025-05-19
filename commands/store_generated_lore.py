"""
commands/store_generated_lore.py

Handles the store_generated_lore CLI command for LoreBuilder after refactoring.
"""
import lore
from rich import print as rprint

def handle(args, context):
    """
    Handles the store_generated_lore CLI command.
    
    Args:
        args (list): Command arguments
        context (dict): Shared context dictionary
    """
    # Call the lore module's store_generated_lore function
    lore.store_generated_lore(args, context)
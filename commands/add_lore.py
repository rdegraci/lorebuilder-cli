
"""
commands/add_lore.py

Handles the add_lore CLI command for LoreBuilder after refactoring.
"""
import lore
from rich import print as rprint
from lore_entities import extract_character_names_from_lore

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

    # After successfully adding lore, re-extract characters from all lore
    try:
        collection = context.get('chroma_collection', None)
        if collection is not None:
            all_docs = collection.get()['documents']
            new_characters = extract_character_names_from_lore(all_docs)
            context['characters_in_lore'] = new_characters
        else:
            rprint("[yellow]Chroma collection not available; characters_in_lore not updated.")
    except Exception as e:
        rprint(f"[yellow]Warning: Failed to update characters_in_lore after adding lore: {e}")




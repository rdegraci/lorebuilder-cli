
"""
commands/store_generated_lore.py

Handles the store_generated_lore CLI command for LoreBuilder after refactoring.
"""
import lore
from rich import print as rprint
from lore_entities import extract_character_names_from_lore

def handle(args, context):
    """
    Handles the store_generated_lore CLI command.
    
    Args:
        args (list): Command arguments
        context (dict): Shared context dictionary
    """
    # Call the lore module's store_generated_lore function
    lore.store_generated_lore(args, context)

    # After successfully storing lore, re-extract characters
    try:
        collection = None
        collection_name = None
        if 'chroma_collection' in context:
            collection = context['chroma_collection']
            collection_name = collection.name if hasattr(collection, 'name') else str(collection)
        if not collection:
            rprint("[yellow]Warning: 'chroma_collection' not found in context.[/yellow]")
        else:
            all_docs = collection.get()
            documents = all_docs.get('documents') if isinstance(all_docs, dict) else None
            if documents is None:
                rprint("[yellow]Warning: 'documents' not found in chroma_collection.get().[/yellow]")
            else:
                names = extract_character_names_from_lore(documents)
                context['characters_in_lore'] = names
    except Exception as e:
        rprint(f"[yellow]Warning: Failed to update 'characters_in_lore' after storing lore: {e}[/yellow]")




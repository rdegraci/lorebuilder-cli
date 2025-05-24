
"""
Command registry for the LoreBuilder CLI application.
This module organizes all available commands and handlers for the CLI interface.
"""

from .add_lore import handle as add_lore
from .generate_lore import handle as generate_lore
from .store_generated_lore import handle as store_generated_lore
from .chat_as import handle as chat_as
from .reset import handle as reset
from .list_characters import handle as list_characters

# Import handlers directly from the modules
import lore

COMMANDS_REGISTRY = {
    # Commands from individual module files
    "add_lore": add_lore,
    "generate_lore": generate_lore,
    "store_generated_lore": store_generated_lore,
    "chat_as": chat_as,
    "reset": reset,
    "list_characters": list_characters,

    # Commands from lore.py
    "query_lore": lore.query_lore,
    "list_all_lore": lore.list_all_lore,
    "delete_lore": lore.delete_lore,
}



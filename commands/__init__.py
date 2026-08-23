
"""
Command registry for the LoreBuilder CLI application.
This module organizes all available commands and handlers for the CLI interface.
"""

from .add_lore import handle as add_lore
from .generate_lore import handle as generate_lore
from .store_generated_lore import handle as store_generated_lore
from .chat_to import handle as chat_to
from .chat_with import handle as chat_with
from .reset_chat import handle as reset_chat
from .list_characters import handle as list_characters

# Import handlers directly from the modules
import lore

COMMANDS_REGISTRY = {
    # Commands from individual module files
    "add_lore": add_lore,
    "generate_lore": generate_lore,
    "store_generated_lore": store_generated_lore,
    "chat_to": chat_to,
    "chat_with": chat_with,
    "reset_chat": reset_chat,
    "list_characters": list_characters,

    # Commands from lore.py
    "query_lore": lore.query_lore,
    "list_all_lore": lore.list_all_lore,
    "delete_lore": lore.delete_lore,
}

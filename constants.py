"""
constants.py

Central constants file for the LoreBuilder CLI application.
Contains all magic numbers, strings, and configuration constants used throughout the application.
"""

# Application constants
APP_NAME = "LoreBuilder CLI"
APP_VERSION = "1.0.0"

# Database constants
DEFAULT_CHAT_DB_FILE = "lore_chat_history.db"
DEFAULT_CHROMADB_PATH = "./chromadb"

# LLM constants
DEFAULT_LLM_MODEL = "openai/gpt-4o-mini"
DEFAULT_MAX_TOKENS = 1024
DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Lore constants
MIN_LORE_ID = 100000
MAX_LORE_ID = 999999
DEFAULT_QUERY_RESULTS = 5
DISPLAY_TEXT_LIMIT = 100
MIN_QUERY_LENGTH = 3

# Chat constants
DEFAULT_CHAT_HISTORY_LIMIT = 20
ROLE_USER = "user"
ROLE_CHARACTER = "character"

# NPC constants
DEFAULT_MAX_NPCS_FOR_SCENE = 3

# Error messages
ERROR_LLM_API_KEY_MISSING = "LLM_API_KEY not set in .env or environment."
ERROR_LORE_SERVICE_NOT_INITIALIZED = "[red]Lore service not initialized. Call init_lore first."
ERROR_EMPTY_CHARACTER_NAME = "Character name cannot be empty"
ERROR_EMPTY_MESSAGE = "Message cannot be empty"
ERROR_EMPTY_NPC_NAME = "NPC name cannot be empty"
ERROR_INVALID_ROLE = "Role must be"
ERROR_NEGATIVE_COUNT = "Count must be non-negative"
ERROR_POSITIVE_LIMIT_REQUIRED = "Limit must be positive"
ERROR_INVALID_LIMIT = "Limit must be positive"

# Chat history error messages
ERROR_DB_INIT_FAILED = "Failed to initialize database"
ERROR_SESSION_OPERATION_FAILED = "Failed to get or create session for character"
ERROR_MESSAGE_ADD_FAILED = "Failed to add message to session"
ERROR_HISTORY_FETCH_FAILED = "Failed to get history for session"
ERROR_HISTORY_RESET_FAILED = "Failed to reset history for session"
ERROR_SESSION_DELETE_FAILED = "Failed to delete session"
ERROR_HISTORY_EXPORT_FAILED = "Failed to export history for session"
ERROR_SESSION_LIST_FAILED = "Failed to list sessions"

# Lore-specific error messages
ERROR_ADDING_LORE = "[red]Error adding lore: {error}"
ERROR_GENERATING_LORE = "[red]Error generating lore: {error}"
ERROR_STORING_LORE = "[red]Error storing generated lore: {error}"
ERROR_QUERYING_LORE = "[red]Error querying lore: {error}"
ERROR_LISTING_LORE = "[red]Error listing lore: {error}"
ERROR_DELETING_LORE = "[red]Error deleting lore: {error}"

# Success messages
SUCCESS_LORE_ADDED = "[green]Lore added with id {id}."
SUCCESS_LORE_STORED = "[green]Stored generated lore with id {id}."
SUCCESS_LORE_DELETED = "[green]Deleted lore entry with ID {id}."

# Warning messages
WARNING_NO_LORE_TO_STORE = "[yellow]No generated lore to store. Use generate_lore first."
WARNING_NO_LORE_FOUND = "[dim]No relevant lore found."

# Info messages
INFO_NO_EXISTING_LORE = "[dim]No lore entries found in the system."
LORE_MODULE_INITIALIZED = "[dim]Lore module initialized.[/dim]"

# Usage messages
USAGE_ADD_LORE = "[yellow]Usage: add_lore <lore_text>"
USAGE_GENERATE_LORE = "[yellow]Usage: generate_lore <user_prompt>"
USAGE_QUERY_LORE = "[yellow]Usage: query_lore <query>"
USAGE_DELETE_LORE = "[yellow]Usage: delete_lore <lore_id>"

# System prompts and templates
DEFAULT_LORE_SYSTEM_PROMPT = "You are a creative worldbuilder."
DEFAULT_PROMPT_TEMPLATE = "You are a creative worldbuilder. Context: {context}"
DEFAULT_LORE_FALLBACK_CONTEXT = "(No existing world lore found. Create something new.)"

# File extensions and patterns
YAML_EXTENSION = ".yaml"
DB_EXTENSION = ".db"
ENV_FILE = ".env"
CONFIG_FILE = "app.yaml"

# CLI constants
CLI_PROMPT = "lore> "
CLI_EXIT_COMMANDS = ["exit", "quit", "q"]
CLI_HELP_COMMANDS = ["help", "h", "?"]

# Display formatting
MAX_DISPLAY_WIDTH = 80
TRUNCATE_SUFFIX = "..."
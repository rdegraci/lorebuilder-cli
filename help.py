"""
help.py - Banner and command/help menu utilities for CLI
"""
from rich import print as rprint
from rich.text import Text

BANNER = (
    "[bold cyan]╔═════════════════════════════════════════════════════════╗\n"
    "║            LoreBuilder CLI - World Builder              ║\n"
    "╚═════════════════════════════════════════════════════════╝[/bold cyan]"
)

LORE_COMMANDS = [
    "add_lore",
    "generate_lore",
    "store_generated_lore",
    "query_lore",
    "list_all_lore",
    "delete_lore",
]
CHAR_COMMANDS = [
    "chat_to",
    "list_characters",
]
SYSTEM_COMMANDS = ["help", "exit"]

COMMAND_HELP = {
    "add_lore": {
        "summary": "Add lore text to the world",
        "usage": "add_lore <lore_text>",
        "description": (
            "Save a lore entry to ChromaDB for semantic search and character extraction. "
            "If no text is provided on the command line, you will be prompted to paste lore."
        ),
        "examples": [
            "add_lore The city of Ardelune is ruled by a council of scholars.",
            "add_lore",
        ],
    },
    "generate_lore": {
        "summary": "Generate new lore with the LLM",
        "usage": "generate_lore <prompt>",
        "description": (
            "Ask the LLM to write new world details. Relevant existing lore is retrieved "
            "automatically and used as context. Generated lore is kept in memory only and is "
            "not saved to the world until you run store_generated_lore."
        ),
        "examples": [
            "generate_lore Describe a festival held by the people of Ardelune.",
            "generate_lore What secrets are rumored about the Order of Shadows?",
            "store_generated_lore",
        ],
    },
    "store_generated_lore": {
        "summary": "Save the last generated lore entry",
        "usage": "store_generated_lore",
        "description": (
            "Persist the most recent output from generate_lore into ChromaDB. "
            "Character names are re-extracted after storing."
        ),
        "examples": [
            "store_generated_lore",
        ],
    },
    "query_lore": {
        "summary": "Search lore by meaning",
        "usage": "query_lore <query>",
        "description": (
            "Find lore entries semantically similar to your query using vector search."
        ),
        "examples": [
            "query_lore council",
            "query_lore Crystal Lake",
        ],
    },
    "list_all_lore": {
        "summary": "List all saved lore entries",
        "usage": "list_all_lore",
        "description": (
            "Show every lore entry with its ID. Long entries are truncated in the display."
        ),
        "examples": [
            "list_all_lore",
        ],
    },
    "delete_lore": {
        "summary": "Delete a lore entry by ID",
        "usage": "delete_lore <lore_id>",
        "description": (
            "Remove a lore entry from ChromaDB. Use list_all_lore to find entry IDs."
        ),
        "examples": [
            "delete_lore 482913",
        ],
    },
    "chat_to": {
        "summary": "Chat with a character using lore-aware context",
        "usage": "chat_to <character_name> <message>",
        "description": (
            "Start or continue a conversation with a character mentioned in world lore. "
            "Supports fuzzy name matching and quoted multi-word names. "
            "Conversation history is saved per character in SQLite."
        ),
        "examples": [
            'chat_to Mara What do you know about the Order of Shadows?',
            'chat_to "The Mage of the Lake" Who visits the lake at midnight?',
        ],
    },
    "list_characters": {
        "summary": "List characters found in lore",
        "usage": "list_characters",
        "description": (
            "Show person names extracted from all saved lore using spaCy NER. "
            "Use chat_to to converse with any listed character."
        ),
        "examples": [
            "list_characters",
        ],
    },
    "help": {
        "summary": "Show command help",
        "usage": "help [command]",
        "description": (
            "Without arguments, shows all available commands. "
            "With a command name, shows detailed usage and examples."
        ),
        "examples": [
            "help",
            "help add_lore",
            "help chat_to",
        ],
    },
    "exit": {
        "summary": "Exit the CLI",
        "usage": "exit",
        "description": "Leave the interactive session.",
        "examples": [
            "exit",
        ],
    },
}


def print_banner():
    """Print the application banner/logo."""
    rprint(BANNER)


def _format_command_line(command: str) -> str:
    """Format a one-line command summary for the menu."""
    info = COMMAND_HELP.get(command, {})
    return info.get("usage", command)


def print_command_menu(commands_registry=None):
    """
    Print available commands by category.
    """
    if commands_registry is None:
        from commands import COMMANDS_REGISTRY
        commands_registry = COMMANDS_REGISTRY

    rprint("[bold cyan]Available Commands:[/bold cyan]")

    categories = [
        ("Lore", LORE_COMMANDS),
        ("Characters", CHAR_COMMANDS),
        ("System", SYSTEM_COMMANDS),
    ]
    for category, command_names in categories:
        lines = [
            _format_command_line(name)
            for name in command_names
            if name in SYSTEM_COMMANDS or name in commands_registry
        ]
        if not lines:
            continue
        rprint(f"[cyan]{category}:[/cyan]")
        for line in lines:
            rprint(f"  [white]{line}[/white]")

    rprint(Text("Type 'help <command>' for details. Example: help add_lore", style="dim"))


def print_command_help(command: str, commands_registry=None):
    """
    Print detailed help for a single command.
    """
    if commands_registry is None:
        from commands import COMMANDS_REGISTRY
        commands_registry = COMMANDS_REGISTRY

    help_info = COMMAND_HELP.get(command)
    if not help_info:
        rprint(f"[red]No such command: {command}[/red]")
        rprint("[dim]Type 'help' to see available commands.[/dim]")
        return

    if command not in commands_registry and command not in SYSTEM_COMMANDS:
        rprint(f"[red]No such command: {command}[/red]")
        rprint("[dim]Type 'help' to see available commands.[/dim]")
        return

    rprint(f"[bold cyan]{command}[/bold cyan] — {help_info['summary']}")
    rprint(f"\n[cyan]Usage:[/cyan] {help_info['usage']}")

    description = help_info.get("description")
    if description:
        rprint(f"\n{description}")

    examples = help_info.get("examples", [])
    if examples:
        rprint("\n[cyan]Examples:[/cyan]")
        for example in examples:
            rprint(f"  {example}")

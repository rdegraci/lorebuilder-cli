
"""
LoreBuilder CLI - A world-building tool that combines vector database storage, 
language models, and SQLite for creating and exploring fictional worlds.
"""

from cli import start_cli
from bootstrap import initialize_app

if __name__ == "__main__":
    context = initialize_app()
    start_cli(context)



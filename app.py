"""
LoreBuilder CLI - A world-building tool that combines vector database storage, 
language models, and SQLite for creating and exploring fictional worlds.
"""

import yaml
import chromadb
from chromadb.utils import embedding_functions
import litellm
from rich import print as rprint
from datetime import datetime
import os
from dotenv import load_dotenv
import chat_history
import sqlite3
import uuid
import json
import random
import traceback
import re
from commands import COMMANDS_REGISTRY
import lore
import locations
import npcs

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# --- Load environment variables ---
load_dotenv()

# --- Load Config ---
with open("app.yaml") as f:
    config = yaml.safe_load(f)

# --- Ensure llm_api_key is read from environment ---
if not os.getenv("LLM_API_KEY"):
    raise EnvironmentError("LLM_API_KEY not set in .env or environment.")
llm_api_key = os.getenv("LLM_API_KEY")

# --- Set default configuration values if not present ---
if "locations_db_path" not in config:
    config["locations_db_path"] = "chat.db"
if "lore_llm_model" not in config:
    config["lore_llm_model"] = config.get("llm_provider", "openai/gpt-4o-mini")
if "lore_llm_system_prompt" not in config:
    config["lore_llm_system_prompt"] = config.get("prompt_template", "You are a creative worldbuilder.")

# --- Init Embedding for lore ---
embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=config["embedding_model"]
)

# --- Init ChromaDB for lore ---
client = chromadb.PersistentClient(path=config["chromadb_path"])
collection = client.get_or_create_collection("lore", embedding_function=embedder)

# --- Init chat DB ---
chat_history.initialize_db()

# --- Pass shared resources to lore and locations modules ---
rprint("[dim]Initializing modules...[/dim]")
lore.init_lore(config=config, chroma_collection=collection, embedder=embedder, 
              llm_api_key=llm_api_key, chat_history=chat_history)
locations.init_locations(config=config, chat_history=chat_history)

def chat_loop():
    """
    Main command-line interface loop, with support for lore, world exploration, and chat commands.
    At start, shows the initial location for the last character from previous sessions.
    """
    rprint("[bold cyan]╔═════════════════════════════════════════════════════════╗")
    rprint("[bold cyan]║            LoreBuilder CLI - World Builder              ║")
    rprint("[bold cyan]╚═════════════════════════════════════════════════════════╝")
    rprint("[bold cyan]Available Commands:")
    rprint("[cyan]Lore: [white]add_lore, generate_lore, store_generated_lore, query_lore, list_all_lore, delete_lore")
    rprint("[cyan]Navigation: [white]look, save_look, go <direction>, reset_location, history")
    rprint("[cyan]Characters: [white]chat_as <character> <message>, reset <character>")
    rprint("[cyan]System: [white]exit")
    
    context = {
        'last_generated_lore': '',
        'last_look_result': None,
    }

    # At script start: show last location for last-used character (if any)
    try:
        # Attempt to discover last character/session
        conn = locations.get_db_connection()
        c = conn.cursor()
        c.execute("SELECT character_name FROM character_location ORDER BY timestamp DESC LIMIT 1")
        row = c.fetchone()
        conn.close()
        if row:
            first_char = row[0]
            scene_info = locations.look(first_char)
            rprint(f"[bold green]Restored location for '{first_char}':")
            rprint(f"[bold magenta]{scene_info['display_name']}[/bold magenta] [grey]({scene_info['location_id']})[/grey]")
            rprint(f"{scene_info['description']}")
            if scene_info['exits']:
                rprint(f"[bold white]Exits:[/bold white] " + ", ".join(scene_info['exits']))
            if "_explanation" in scene_info and scene_info["_explanation"]:
                rprint(f"[dim][Reason:] {scene_info['_explanation']}[/dim]")
            context['last_look_result'] = scene_info
    except Exception as e:
        # Ignore if table empty or on error
        rprint(f"[dim]Note: {str(e)}[/dim]")
    
    rprint("[cyan]Ready! Enter commands below:[/cyan]")
    
    while True:
        try:
            cmd = input(">> ").strip()
            if cmd == "exit":
                break
            
            tokens = cmd.split()
            if not tokens:
                continue
                
            command = tokens[0]
            args = tokens[1:] if len(tokens) > 1 else []
            
            # Handle commands with or without leading slash
            canonical_command = command.lstrip('/')
            
            # Find the handler in the registry
            handler = COMMANDS_REGISTRY.get(canonical_command)
            
            if handler:
                handler(args, context)
            else:
                rprint(f"[red]Unknown command: {command}. Type a command from the list above.")
        except Exception as e:
            traceback.print_exc()
            rprint(f"[red]Error processing command: {str(e)}")

if __name__ == "__main__":
    chat_loop()
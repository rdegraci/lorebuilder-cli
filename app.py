
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
from cli import start_cli

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

if __name__ == "__main__":
    context = {
        'last_generated_lore': '',
        'last_look_result': None,
    }
    start_cli(context)



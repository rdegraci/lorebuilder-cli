
"""
bootstrap.py

App initialization module for LoreBuilder CLI.
Sets up config, env, embedding, vector DB, chat DB, and modules.
"""
import yaml
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import os
from rich import print as rprint
import chat_history
import lore
import lore_entities
from lore_entities import extract_character_names_from_lore


def initialize_app():
    """
    Bootstraps configuration, environment variables, DBs, and module dependencies.
    Returns a context dict for use by the CLI.
    """
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    load_dotenv()
    rprint("[dim]Loading configuration and environment...[/dim]")

    # Load config
    with open("app.yaml") as f:
        config = yaml.safe_load(f)
    if "lore_llm_model" not in config:
        config["lore_llm_model"] = config.get("llm_provider", "openai/gpt-4o-mini")
    if "lore_llm_system_prompt" not in config:
        config["lore_llm_system_prompt"] = config.get("prompt_template", "You are a creative worldbuilder.")

    # Environmental config
    if not os.getenv("LLM_API_KEY"):
        raise EnvironmentError("LLM_API_KEY not set in .env or environment.")
    llm_api_key = os.getenv("LLM_API_KEY")

    # Embedding init
    embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=config["embedding_model"]
    )

    # Chroma DB init
    client = chromadb.PersistentClient(path=config["chromadb_path"])
    collection = client.get_or_create_collection("lore", embedding_function=embedder)

    # Chat DB
    chat_history.initialize_db()

    # Module dependency injection
    rprint("[dim]Initializing modules...[/dim]")
    lore.init_lore(config=config, chroma_collection=collection, embedder=embedder,
                  llm_api_key=llm_api_key, chat_history=chat_history)
    # npcs module is stateless

    # Extract lore documents and character names
    try:
        lore_docs = collection.get().get('documents', [])
        characters_in_lore = extract_character_names_from_lore(lore_docs)
    except Exception as e:
        rprint(f"[yellow]Warning: Could not extract character names from lore. {e}[/yellow]")
        characters_in_lore = set()

    context = {
        'config': config,  # pass to CLI if handlers wish to use
        'last_generated_lore': '',
        'last_look_result': None,
        'characters_in_lore': characters_in_lore,
        'chroma_collection': collection,
    }
    return context




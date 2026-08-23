
"""
bootstrap.py

App initialization module for LoreBuilder CLI.
Sets up config, env, embedding, vector DB, chat DB, and modules.
"""
import shutil
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
from constants import CONFIG_FILE, ENV_FILE

CONFIG_EXAMPLE = "app.yaml.example"
ENV_EXAMPLE = ".env.example"
ENV_API_KEY_PLACEHOLDER = "your-model-api-key-here"


def _create_file_from_example(target: str, example: str, fallback_content: str) -> None:
    """Create target file from example template, or fallback content if example is missing."""
    if os.path.exists(example):
        shutil.copyfile(example, target)
    else:
        with open(target, "w") as f:
            f.write(fallback_content)
    rprint(f"[green]Created {target}[/green]")


def _ensure_env_file() -> None:
    """Create .env from .env.example on first run if it does not exist."""
    if os.path.exists(ENV_FILE):
        return
    _create_file_from_example(
        ENV_FILE,
        ENV_EXAMPLE,
        f"LLM_API_KEY={ENV_API_KEY_PLACEHOLDER}\n",
    )
    rprint(f"[yellow]Edit {ENV_FILE} and set LLM_API_KEY before using LLM features.[/yellow]")


def _ensure_config_file() -> None:
    """Create app.yaml from app.yaml.example on first run if it does not exist."""
    if os.path.exists(CONFIG_FILE):
        return
    _create_file_from_example(
        CONFIG_FILE,
        CONFIG_EXAMPLE,
        (
            "chromadb_path: ./chromadb\n"
            "embedding_model: all-MiniLM-L6-v2\n"
            "llm_provider: openai/gpt-4o-mini\n"
            "lore_llm_model: openai/gpt-4o-mini\n"
            "prompt_template: >\n"
            "  You are a creative worldbuilder. Use this existing lore as context:\n"
            "  {context}\n"
            "chat_prompt_template: >\n"
            "  You are {character_name}, a character in a fictional world.\n"
            "  Stay in character. Use this lore as context:\n"
            "  {context}\n"
            "cli_history_path: .lorebuilder_cli_history\n"
        ),
    )


def initialize_app():
    """
    Bootstraps configuration, environment variables, DBs, and module dependencies.
    Returns a context dict for use by the CLI.
    """
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    _ensure_env_file()
    _ensure_config_file()
    load_dotenv()
    rprint("[dim]Loading configuration and environment...[/dim]")

    # Load config
    with open(CONFIG_FILE) as f:
        config = yaml.safe_load(f)
    if "lore_llm_model" not in config:
        config["lore_llm_model"] = config.get("llm_provider", "openai/gpt-4o-mini")
    if "lore_llm_system_prompt" not in config:
        config["lore_llm_system_prompt"] = config.get("prompt_template", "You are a creative worldbuilder.")

    # Environmental config
    llm_api_key = os.getenv("LLM_API_KEY")
    if not llm_api_key or llm_api_key == ENV_API_KEY_PLACEHOLDER:
        raise EnvironmentError(
            f"LLM_API_KEY not set. Edit {ENV_FILE} and add your API key."
        )

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




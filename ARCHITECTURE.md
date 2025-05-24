
# LoreBuilder Developer Architecture Reference (2024)

**Audience:** For onboarding and orienting new developers to the LoreBuilder CLI codebase.

---

## 1. System Overview

LoreBuilder is a modular CLI application for RAG-powered conversational world-building. It supports persistent character chat, semantic lore search, and LLM-driven dialog, all presented via a command registry architecture and terminal UI.

---

## 2. Core Workflow

### a) app.py (Entrypoint)
- Loads the world and all modules via `bootstrap.initialize_app()`
- Immediately launches CLI loop (`cli.start_cli(context)`)

### b) bootstrap.py (Application Initialization)
- Loads configuration (`app.yaml`) and secrets (`.env`)
- Verifies all needed LLM, embedding, and data storage models are present
- Sets up:
    - Persistent ChromaDB collection for vector search/lore
    - Embedding models (SentenceTransformer)
    - Chat/session DB for replayable histories (SQLite/ chat_history.py)
    - Master LLM/config/event service (`LoreService` in lore.py)
    - NLP entity extraction for dynamic character list (spaCy/rapidfuzz)

- Returns a global `context` dict with all active resources and live world info

### c) cli.py (CLI Loop)
- Prints banner, reads/presents available commands from registry
- Parses user input, resolves to canonical command, passes to handler with shared context
- Handles help, error, and info messages consistently (via cli_utils.py)

### d) commands/ (Command Modules)
- Each handler implements a single CLI entrypoint (e.g., add_lore, chat_as, list_characters)
- All command handlers are centrally registered in commands/__init__.py
- Dynamic help and menu loading—only active and maintained commands appear in UI/menus (`help` relies on docstrings)
- All deprecated modules such as locations.py and npcs.py are now entirely decoupled and safe to remove

---

## 3. Core Data Flows

- **World/Lore:** Managed exclusively by ChromaDB + embeddings for retrieval, and always in sync for entity extraction (characters).
- **Chat:** All messages are routed through core SQLite persistence for multi-turn, sessionized replay/support.
- **LLM:** Only via the LoreService class (no scattered API keys/configs)
- **Character/Entity Extraction:** spaCy and rapidfuzz, invoked on world/lore data and user messaging to keep chat_as flexible and robust (supports quoted, fuzzy, full/partial, and multi-word character names)

---

## 4. File and Module Map

- **app.py** — Entrypoint, loads all dependencies, and drops to CLI
- **bootstrap.py** — All startup logic/services/context initialization
- **cli.py** — CLI and command input/repl
- **help.py, cli_utils.py** — Banner, help, consistent outputs
- **commands/** — All registered CLI command handlers, one per file, registry maintained in __init__.py
- **lore.py** — LoreService, LLM integration, embeddings, all RAG logic, and active world state
- **lore_entities.py** — All character/entity extraction and fuzzy matching
- **chat_history.py** — Session chat persistence

---

## 5. Extensibility Pointers

- **To add a command:** Write handler in commands/, add to __init__.py
- **To adjust world/LLM config:** Edit bootstrap.py and/or LoreService config in lore.py
- **To change entity extraction:** Update logic in lore_entities.py

---

## 6. Onboarding and Upgrading

- `pip install -r requirements.txt`
- `python -m spacy download en_core_web_sm`
- Configure `.env` for LLM API keys
- Launch with `python app.py`
- Run `help` or `help <command>` for current list and handler documentation

---

## 7. Deprecations

- The locations.py and npcs.py modules are no longer referenced or registered; their logic is not used in the current CLI, command registry, or world data model, and are safe to delete.

---

_This summary is up to date as of 2024. See command docstrings or bootstrap.py for further detail, or CLI menus for active capability._



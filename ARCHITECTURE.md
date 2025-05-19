# LoreBuilder Architecture (2024 Update)

LoreBuilder is a hybrid Retrieval-Augmented Generation (RAG) world-building CLI, engineered for persistent, replayable, and lore-rich conversational experiences. The system integrates:

- SQLite-backed multi-turn chat and location/session history,
- ChromaDB-powered vector search for scene/lore,
- LLM-driven logic for contextual storytelling and dynamic world navigation.

This document targets code reviewers needing a high-level and practical grasp of system structure, data flows, and extensibility.

---

## 1. Key Features

- **Multi-turn Chat:** Supports per-character tracked, persistent conversations—stored in SQLite for reliability and replay.
- **Location/Scene System:** Dual-persistence design: relational (SQLite tables: `character_location`, `location_entries`) for session/canonical tracking, and vector (ChromaDB) for flexible, semantic lore lookup.
- **LLM-driven Assignment:** When spawning new characters, context-aware LLM selects (or generates) location assignments, falling back to random canonical sites if needed.
- **Scene Lore Canonicalization:** Scenes and exits can be permanently 'saved' or indexed for canonical or non-canonical retrieval.
- **Interactive CLI:** Modular command registry, help, and error systems allow rapid CLI evolution, scene navigation, lore addition, chat, and world inspection.

---

## 2. Components Overview

### 2.1. Initialization (`bootstrap.py`)
- Handles configuration, environment loading, ChromaDB, embedding, database initialization, and module injection in a single place.
- Entry point for bootstrapping the application before handing off to the CLI loop.

### 2.2. CLI Loop & Parsing (`cli.py`)
- Orchestrates user interaction, command input, context management, and handler dispatch.
- Leverages a centralized command registry for extensibility.
- Handles only the CLI UI—separated from all domain logic.

### 2.3. Banner/Help/Menu (`help.py`)
- Renders the CLI ASCII banner, command listing, and per-command help from handler docstrings.
- Shows dynamic help based on the command registry (`help`/`help <command>` commands).

### 2.4. Centralized CLI Output (`cli_utils.py`)
- Ensures consistent, branded output for error, success, warning, and info messages.
- Provides reusable helpers for all user-facing CLI messaging with styling.

### 2.5. Command Registry (`commands/` directory)
- Directory of modular, single-responsibility command handlers.
- `commands/__init__.py` builds the `COMMANDS_REGISTRY` mapping command names to handlers.
- Enables drop-in addition or updating of user-available CLI commands.

### 2.6. Lore Handling (`lore.py`), Location Logic (`locations.py`), NPCs, Chat (`chat_history.py`)
- Each core feature is modular and initialized via shared resources from the bootstrap context.
- Lore and locations are persistent, LLM/embedding enhanced, and support both relational and vector-based querying.

---

## 3. Data & Workflow Outline

- **Bootstrapping a World/Session:** Uses `bootstrap.py` to prepare config, ChromaDB, embedding, chat DB, and all feature modules.
- **CLI Launch:** `app.py` simply calls `initialize_app()` (bootstrap) and `start_cli(context)` (CLI loop).
- **User Command Handling:** All commands are parsed and dispatched dynamically from the registry. Help and messaging are standardized.
- **Chat/Session Persistence:** Every exchange (user or LLM) is logged in `chat_history.db` and can be replayed.
- **Location Query/Update:** Scene changes update both relational and vector mapping.
- **Scene Saving:** Lore and scene data are stored in both SQL and vector/embedding stores as appropriate.

---

## 4. Extensibility and Maintainability

- The modular design supports new commands, output formats, or bootstrapping options without impact to mainline logic.
- CLI output/messages and help are all centralized and can be themed or internationalized.
- All modules are decoupled from the CLI and interact only through passed-in dependencies/context.
- The command registry system ensures easy discovery and documentation.

---

## 5. Dependencies

- [ChromaDB](https://www.trychroma.com/) (semantic vector storage)
- [LiteLLM](https://github.com/BerriAI/litellm) (LLM API abstraction)
- [Rich](https://github.com/Textualize/rich) (CLI feedback)
- [sqlite3](https://docs.python.org/3/library/sqlite3.html) (persistent chat/location/lore history)
- [python-dotenv](https://github.com/theskumar/python-dotenv) (environment loading)

---

## 6. File/Schema Overview

- `app.py` — Minimal entrypoint, launches bootstrap then CLI
- `bootstrap.py` — All configuration, env, embedding, vector DB, and module setup
- `cli.py` — CLI input loop, command parsing, user interaction, and context control
- `help.py` — Banner, command menu, and dynamic help utilities
- `cli_utils.py` — Consistent output for error, warning, info, and success
- `commands/` — Modular directory with individual CLI command handler modules and the global registry
- `lore.py` — Lore/scene logic, embedding, LLM generation, and vector operations
- `locations.py` — Location creaton/query/movement, canonical and non-canonical state tracking
- `npcs.py` — Plausible NPC population for scenes
- `chat_history.py` — SQLite multi-turn chat/session engine
- `*.db` — Persistent chat/location/lore data (SQLite)
- `chromadb/` — Vector/semantic lore descriptions (ChromaDB)
- `ARCHITECTURE.md` — (This file)
- `app.yaml` — Config (models, prompts, data paths)
- `.env` — LLM and secret config

---

## 7. Reviewer Notes
- All persistent world, chat, and lore state is forward-migration safe and replayable.
- Vector+relational hybrid enables fast semantic querying while retaining story/world integrity via canonical RDBMS state.
- CLI output, help, and error handling are now modular and consistent across commands and workflows.
- Guidance for LLM context/context pruning, rapid location assignment, and extensibility points is embedded in code comments.
- See tests and command help for worked CLI/data examples.

_This document supersedes earlier summaries with details on the modular CLI, command registry, and centralized output architecture._

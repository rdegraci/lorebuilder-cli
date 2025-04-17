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
- **Interactive CLI:** Command loop enables scene navigation, lore addition, chat overview, replay, and migration/testing workflows.

---

## 2. Components Overview

### 2.1. Chat History (`chat_history.py`)
- Each CLI user/character pair has its own session history in SQLite.
- System enables session replay, deletion, and automatic log updating on every user/LLM exchange.
- Chat entries include role, text, timestamp, and relevant location/session.

### 2.2. Location Management
- **Relational Layer:** Tracks canonical scenes, locations, and their mapping to sessions/users. Includes schema for location names, canonical status, and associated exits.
- **Semantic Lore Layer:** Canonical/non-canonical descriptions and exits are stored with embeddings in ChromaDB—allowing flexible, vector-based retrieval for scene recall/expansion.

### 2.3. LLM Orchestration
- Location assignment is handled by LLM (with lore/context seed), with fallback logic to canonical/random location list.
- Dialogue continues based on per-character history/context.
- `/save_look` and similar commands trigger save/query workflows coupling CLI, SQLite, and ChromaDB.

### 2.4. CLI Experience (`app.py`)
- Supports enhanced lore bootstrapping, history navigation, and in-world chat via command loop.
- Integrates migration and test touchpoints for database and vector store evolution.

---

## 3. Data & Workflow Outline

- **Bootstrapping a World/Session:** Loads canonical locations and lore. Optionally generates locations/scenes via LLM if missing.
- **Chat/Session Persistence:** Every exchange (user or LLM) is logged in `chat_history.db` and can be replayed.
- **Location Query/Update:** On scene changes, updates both relational mapping and optionally generates vector-based lore/description.
- **Scene Saving:** `/save_look` invokes context-aware save to both SQLite (as canonical/non-canonical scene) and vector DB.

---

## 4. Extensibility and Maintainability

- All database schema changes are handled with built-in migration flows; new location/chat features are readily extendable.
- Supports plug-and-play LLM “decision” logic for location assignment, context pruning, and lore seeding.
- CLI loop designed for drop-in of new commands, including developer/testing/operator hooks.

---

## 5. Dependencies

- [ChromaDB](https://www.trychroma.com/) (semantic vector storage)
- [LiteLLM](https://github.com/BerriAI/litellm) (LLM API abstraction)
- [Rich](https://github.com/Textualize/rich) (CLI feedback)
- [sqlite3](https://docs.python.org/3/library/sqlite3.html) (persistent chat/location/lore history)
- [python-dotenv](https://github.com/theskumar/python-dotenv) (environment loading)

---

## 6. File/Schema Overview

- `app.py` — CLI main loop, command parsing, session state
- `chat_history.py` — SQLite multi-turn chat/session engine
- `lore_chat_history.db` — Persistent multi-user/session chat and world state
- `state.db` — Canonical/non-canonical scene & location mapping
- `chromadb/` — Embedded lore and scene descriptions (embeddings, vector search)
- `ARCHITECTURE.md` — (This file)
- `app.yaml` — Config (models, prompts, data paths)
- `.env` — LLM and secret config

---

## 7. Reviewer Notes
- All persistent world, chat, and lore state is forward-migration safe and replayable.
- Vector+relational hybrid enables fast semantic querying while retaining story/world integrity via canonical RDBMS state.
- CLI includes utilities for inspecting, migrating, or extending the world model and session logs.
- Guidance for LLM context/context pruning, rapid location assignment, and extensibility points is embedded in code comments.
- See tests and command help for worked CLI/data examples.

_This replaces historic RAG-centric summaries with explicit context about persistent memory, world chat, hybrid storage, and extensibility. Direct reviewer questions to code comments or the maintainer._

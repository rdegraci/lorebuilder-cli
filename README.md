# LoreBuilder CLI

A world-building CLI for persistent, replayable, and context-rich conversations. LoreBuilder uniquely combines Retrieval-Augmented Generation (RAG), vector search (ChromaDB), relational (SQLite) world tracking, and LLM-powered story expansion.

---

## Features

- **Multi-Turn Chat History:** All in-world conversations are sessioned, tracked, and replayable (SQLite).
- **Location/Scene System:** Dual-layer canonical/non-canonical location entries combine SQL mapping and vector-embedded lore.
- **LLM-driven Session Context:** Context-aware stories, location assignment, and lore bootstrapping.
- **Semantic Search:** Retrieve, expand, or generate lore fragments using ChromaDB vector search for contextual richness.
- **Extensible In-World CLI:** Navigation, saving canonical scenes, migrating/upgrading logic, and developer/test workflows.
- **Rich Terminal UX:** Colorful, user-friendly feedback powered by Rich.

---

## Quickstart

### 1. Install requirements

```bash
pip install -r requirements.txt
```

### 2. Configure

- Edit `app.yaml`: LLM models, embeddings, ChromaDB path, prompts, etc.
- Add your LLM API key(s) to `.env`:
  ```
  LLM_API_KEY=your-model-api-key-here
  ```
- `.env` is in `.gitignore` by default.

### 3. Run the CLI

```bash
python app.py
```

---

## Core CLI Commands

- `add_lore <text>` — Store lore fragments or scene/place descriptions
- `generate_lore <query>` — Expand lore using RAG+LLM
- `store_generated_lore` — Save the last generated lore
- `/save_look` — Canonicalize and embed current scene look/desc
- `show_chat <character>` — View/replay character sessions
- Scene and navigation commands (move, location assignment, etc.)
- `exit` — Quit

_See shell help or `ARCHITECTURE.md` for more._

---

## Persistent World Model

- **Session & Chat:** All character and user chats are stored in `lore_chat_history.db`.
- **Location/Scene Tracking:** Locations and canonical states in `state.db` (SQLite). Scene/lore descriptions and exits in persisted ChromaDB vector store.
- **Extensible Design:** Add new world/scene/character logic, migratable schema, and developer hooks for bootstrapping worlds or CLI-driven upgrades.

---

## File Structure

- `app.py` — CLI entry, session orchestration, commands
- `chat_history.py` — Chat persistence and replay logic
- `lore_chat_history.db` — Persistent chat/session store
- `state.db` — Canonical location/scene map
- `chromadb/` — Vector search content (lore/scene embeddings)
- `ARCHITECTURE.md` — Design & data-flow docs
- `app.yaml` — LLM, embedding, and prompt config
- `.env` — LLM API config (NEVER COMMIT)
- `requirements.txt` — Dependencies

---

## Dependencies

- ChromaDB — Semantic vector lore search
- SQLite3 — Persistent chat/location logs
- LiteLLM — Unified LLM API provider
- Rich — CLI user experience
- python-dotenv — Environment loading
- PyYAML — YAML parsing/config

---

## Security & Best Practices

- API keys in `.env`, **never** source code.
- All state/world data migratable and forward-compatible.
- Fast semantic search is paired with canonical relational world-model for full integrity.

---

## Documentation & Help

- **For full system design:** See [ARCHITECTURE.md](ARCHITECTURE.md)
- **CLI commands:** Run `help` in the CLI or view code comments.

---

## License

MIT (see LICENSE)

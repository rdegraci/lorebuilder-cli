# LoreBuilder CLI

A world-building CLI for persistent, replayable, and context-rich conversations. LoreBuilder uniquely combines Retrieval-Augmented Generation (RAG), vector search (ChromaDB), relational (SQLite) world tracking, and LLM-powered story expansion.

---

## Features

- **Multi-Turn Chat History:** All in-world conversations are sessioned, tracked, and replayable (SQLite).
- **Location/Scene System:** Dual-layer canonical/non-canonical location entries combine SQL mapping and vector-embedded lore.
- **LLM-driven Session Context:** Context-aware stories, location assignment, and lore bootstrapping.
- **Semantic Search:** Retrieve, expand, or generate lore fragments using ChromaDB vector search for contextual richness.
- **Extensible Modular CLI:** Modular commands, centralized help/menus, and consistent error/info output.
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

## Core CLI Usage

- Modular CLI with dynamic help: type `help` for commands, or `help <command>` for detailed docs.
- Categories:
  - **Lore:** `add_lore`, `generate_lore`, `store_generated_lore`, `query_lore`, `list_all_lore`, `delete_lore`
  - **Navigation:** `look`, `save_look`, `go`, `reset_location`, `history`
  - **Characters:** `chat_as`, `reset`
  - **System:** `help`, `exit`
- All commands and descriptions are auto-discovered from the command registry and module docstrings.

---

## Persistent World Model

- **Session & Chat:** All character and user chats are stored in `lore_chat_history.db`.
- **Location/Scene Tracking:** Locations and canonical states in `state.db` (SQLite). Scene/lore descriptions and exits in persisted ChromaDB vector store.

---

## File Structure

- `app.py` — Minimal entry point (calls bootstrap then CLI)
- `bootstrap.py` — Configuration, env, embedding, DB, and module setup
- `cli.py` — Main CLI loop, user interaction, command dispatch
- `help.py` — Banner/help/menu utilities and automatic command docs
- `cli_utils.py` — Consistent output (error, warning, info, success)
- `commands/` — One file per CLI command; registry for dispatch
- `lore.py` — Lore/scene storage, embedding, and LLM integration
- `locations.py` — Location logic, position/state management
- `npcs.py` — NPC suggestion and world population
- `chat_history.py` — SQLite multi-turn chat/session engine
- `*.db` — Chat/location/lore state
- `chromadb/` — Vector store for lore/scene
- `app.yaml` — Configuration for LLM, embedding, etc
- `.env` — LLM API config (**never commit!**)
- `ARCHITECTURE.md` — System overview

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

- API keys in `.env`, **never** in code.
- Data is migratable and forward-compatible.
- Semantic vector search is paired with relational model for integrity.

---

## Documentation & Help

- **For design/architecture:** See [ARCHITECTURE.md](ARCHITECTURE.md)
- **For CLI commands:** Run `help` or `help <command>` inside the CLI.

---

## License

MIT (see LICENSE)

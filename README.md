
# LoreBuilder CLI

A modular, persistent CLI for world-building and replayable, context-rich character conversations. Combines Retrieval-Augmented Generation (RAG), ChromaDB vector search, SQLite chat history, and LLM-powered story expansion within a robust, developer-friendly command framework.

---

## Features

- **Persistent Multi-Turn Chat** – All conversations replayable via transactional SQLite logging.
- **Semantic Lore Search** – Contextual retrieval via ChromaDB vector DB and modern embeddings.
- **LLM-Driven Stories** – All generation/context managed via a master LoreService and LiteLLM.
- **NLP-Powered Character Recognition** – Flexible, quoted, multi-word, and fuzzy chat with lore-synced character list, powered by spaCy/rapidfuzz.
- **Modular Command Registry & Dynamic Help** – Only active commands appear in help/menus; per-command docs from handler docstrings.
- **Rich Terminal UI** – User-centric, colorized feedback with Rich.

---

## Quickstart

### 1. Install requirements

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Configuration

- Edit `app.yaml` for LLM, embedding, ChromaDB path, prompts, etc.
- Add your LLM API key in `.env` file (never commit this!):
  ```
  LLM_API_KEY=your-model-api-key-here
  ```

### 3. Launch

```bash
python app.py
```

---

## CLI Usage

- Type `help` or `help <command>` for the auto-generated command list and documentation.
- Categories:
  - **Lore:** `add_lore`, `generate_lore`, `store_generated_lore`, `query_lore`, `list_all_lore`, `delete_lore`
  - **Characters:** `chat_as`, `list_characters`
  - **System:** `help`, `exit`
- Only currently active, supported commands are listed.

---

## Persistent World Model

- **Chat:** All character and session logs in `lore_chat_history.db` (SQLite).
- **Lore:** All scene, character, and context lore in ChromaDB vector storage; kept in sync with entity extraction for robust querying.

---

## Project Structure

- `app.py` — Entry point; loads context then starts CLI.
- `bootstrap.py` — Loads all dependencies/services; builds live context.
- `cli.py` — CLI REPL and UX loop.
- `help.py`, `cli_utils.py` — Centralized banner, dynamic help, and output styling.
- `commands/` — Modular CLI command handlers; dynamic registry.
- `lore.py` — LoreService (LLM, embedding, vector logic, config).
- `lore_entities.py` — Character/entity extraction, NLP, and fuzzy matching.
- `chat_history.py` — Persistent, replayable chat/session tracking.
- `app.yaml` — Configuration.
- `.env` — API keys (**never commit!**)
- `ARCHITECTURE.md` — In-depth developer architecture doc.

---

## Dependencies

- ChromaDB (semantic vector search)
- SQLite3 (persistent chat logs)
- LiteLLM (unified LLM API)
- spaCy / en_core_web_sm (NLP for entity detection)
- rapidfuzz (fuzzy matching)
- Rich (CLI experience)
- python-dotenv, PyYAML

---

## Best Practices

- API keys go only in `.env` (never source control).
- Use pip and spaCy model install for all onboarding.
- World and chat state is forward-compatible; modular design supports add/remove commands with confidence.

---

## Documentation

- See [ARCHITECTURE.md](ARCHITECTURE.md) for technical and onboarding guidance.
- Run `help` within the CLI for command-level docs.

---

## License

MIT (see LICENSE)



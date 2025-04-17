# LoreBuilder CLI

A Retrieval-Augmented Generation (RAG) powered lore-building command-line application. Effortlessly create, store, search, and generate new lore using leading LLMs, powerful vector search (ChromaDB), and semantic embeddings.

---

## Features
- **Add Lore:** Store story fragments or world-building notes.
- **Semantic Search:** Retrieve related lore via embeddings + ChromaDB.
- **Generate Lore:** Use LLMs to expand worlds contextually.
- **Store Generated Lore:** Review and save generated text for future use.
- **Rich CLI UI:** User-friendly, color-enhanced terminal output.

---

## Quickstart

### 1. Install requirements
```bash
pip install -r requirements.txt
```

### 2. Configure
- Fill in `app.yaml` with desired LLM provider/model info, embedding settings, and prompt templates.
- Create a `.env` file and add your LLM API key:
  ```
  LLM_API_KEY=your-model-api-key-here
  ```

### 3. Run the CLI
```bash
python app.py
```

---

## CLI Commands
- `add_lore <lore text>` — Add lore to ChromaDB
- `generate_lore <query>` — Generate new lore using RAG and LLM
- `store_generated_lore` — Store last generated lore
- `exit` — Exit the CLI

---

## System Architecture
See [ARCHITECTURE.md](ARCHITECTURE.md) for a breakdown of the app’s logic, data flow, and extensibility.

---

## File Structure
- `app.py` — Main CLI app
- `app.yaml` — Config file for models, prompts, DB path
- `.env` — DO NOT COMMIT: holds secrets like `LLM_API_KEY`
- `requirements.txt` — Python dependencies
- `ARCHITECTURE.md` — Design & Architecture docs

---

## Dependencies
- ChromaDB — Vector search DB
- LiteLLM — Unified interface for LLMs
- Rich — Enhanced CLI UX
- python-dotenv — Secure env var loading
- PyYAML — Config parsing

---

## Security
- Never store API keys in source code or checked-in configs.
- Use `.env` for secrets, and add `.env` to your `.gitignore`.

---

## License
MIT. See LICENSE for details.

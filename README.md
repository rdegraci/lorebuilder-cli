
# LoreBuilder CLI

> **A modular, persistent CLI for world-building and replayable, context-rich character conversations powered by LLMs, ChromaDB, and NLP.**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)

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

```bash
git clone https://github.com/yourusername/lorebuilder-cli.git
cd lorebuilder-cli
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python app.py
```

On first run, `app.yaml` and `.env` are created automatically from the example files. Edit `.env` and set your `LLM_API_KEY` before using LLM features. Edit `app.yaml` if you want to change models, prompts, or storage paths.

---

## Usage

- Type `help` or `help <command>` inside the CLI.
- Example command categories:
  - **Lore:** `add_lore`, `generate_lore`, `store_generated_lore`, `query_lore`, `list_all_lore`, `delete_lore`
  - **Characters:** `chat_to`, `chat_with`, `list_characters`
  - **System:** `help`, `exit`

---

## Directory Structure

```text
app.py               # Main entrypoint
bootstrap.py         # Service initialization
cli.py               # CLI REPL and UX
help.py, cli_utils.py# Help & output styling
commands/            # Modular command handlers
lore.py              # LoreService logic
lore_entities.py     # Entity extraction and NLP
chat_history.py      # Chat/session tracking
app.yaml             # Configuration (auto-created on first run)
app.yaml.example     # Example configuration template
.env                 # API keys (auto-created on first run; never commit)
.env.example         # Example API key file
ARCHITECTURE.md      # Dev architecture doc
```

---

## Persistent World Model

- **Chat:** `lore_chat_history.db` (SQLite)
- **Lore:** ChromaDB vector storage, kept in sync with entity extraction

---

## Dependencies

- ChromaDB, SQLite3, LiteLLM, spaCy, rapidfuzz, Rich, python-dotenv, PyYAML

---

## Documentation

- See [ARCHITECTURE.md](ARCHITECTURE.md)
- In-app `help`

---

## Contributing

Pull requests welcome! Please open issues for bugs or feature requests.

---

## Credits

- **Significant Contributors:**
  - [Anthropic](https://anthropic.com/) - Claude 3.7 and Claude 4 
  - [OpenAI](https://openai.com/) - ChatGPT 4.1

- **Inspirations & Foundations:**
  - [ChromaDB](https://www.trychroma.com/) — Vector database design and docs
  - [spaCy](https://spacy.io/) — NLP entity recognition pipeline
  - [Rich](https://github.com/Textualize/rich) — Terminal formatting and interactive UI

---

## Contact

- Rodney Degracia [https://rodneydegracia.com](https://rodneydegracia.com)
- Email: rdegraci@gmail.com
- Linked In: [https://www.linkedin.com/in/rdegraci/](https://www.linkedin.com/in/rdegraci/)
- GitHub Issues: [https://github.com/yourusername/lorebuilder-cli/issues](https://github.com/yourusername/lorebuilder-cli/issues)

---

## License

MIT (see LICENSE)



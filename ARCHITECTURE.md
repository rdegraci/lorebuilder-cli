# LoreBuilder Architecture

LoreBuilder is a Retrieval-Augmented Generation (RAG) powered CLI tool for lore-building. It integrates natural language generation (LLMs), vector search (ChromaDB), and a configuration-driven interface for interactive story or world-building tasks.

---

## 1. High Level Overview

- **Domain:** Interactive lore creation and management
- **Main Features:**
  - Add lore snippets to a persistent vector database
  - Retrieve and generate lore contextually using LLMs
  - Store both human- and machine-generated lore with full context
  - Command-Line Interface (CLI) for user interaction

---

## 2. Components

### 2.1. Configuration and Secrets
- **app.yaml:**
  - Contains settings for the LLM provider, embedding model, ChromaDB storage path, and prompt template.
- **.env:**
  - Stores sensitive secrets, notably `LLM_API_KEY`, loaded securely at runtime.

### 2.2. Embedding and Vector Store
- **Embedding Function:**
  - Uses `SentenceTransformerEmbeddingFunction` to convert lore text into dense vectors for semantic search.
- **ChromaDB Integration:**
  - Persistent client with a 'lore' collection for storing, querying, and retrieving documents.
  - Requires non-empty metadata (timestamp by default).

### 2.3. LLM Integration
- **Provider:**
  - LLM is invoked through [LiteLLM](https://github.com/BerriAI/litellm), which abstracts different LLM backends.
  - Prompt incorporates previously stored/retrieved lore as context.

### 2.4. CLI (app.py Entry Point)
- **Core Commands:**
  - `add_lore`: Add custom lore to the vector DB.
  - `generate_lore`: Use RAG to generate new lore based on a topic/query.
  - `store_generated_lore`: Store the last generated lore into the DB.
- **Feedback:** Uses [Rich](https://github.com/Textualize/rich) for colored, user-friendly output.
- **Flow:** Command loop parses user input, routes calls to functions, and handles errors/feedback interactively.

---

## 3. Data Flow

1. **Add Lore Command:**
   - User inputs text → embed → store in ChromaDB with metadata
2. **Generate Lore Command:**
   - User query → semantic search in ChromaDB for context → LLM prompt generation → LLM response
3. **Store Generated Lore:**
   - Takes the LLM response → stores as new lore entry in ChromaDB

---

## 4. Security and Best Practices
- Secrets (LLM API keys) never stored in code/config; always loaded from environment.
- All vector DB writes include metadata for traceability.
- Error handling covers missing settings, unknown commands, and misconfigurations.

---

## 5. Extensibility
- LLM backend configurable via app.yaml
- Prompt templates easily swappable
- New commands can be added to the CLI loop as needed
- Embedding models and Chroma settings can be adjusted without code changes

---

## 6. Dependencies
- [ChromaDB](https://www.trychroma.com/) (vector storage)
- [LiteLLM](https://github.com/BerriAI/litellm) (LLM abstraction)
- [Rich](https://github.com/Textualize/rich) (CLI styling)
- [python-dotenv](https://github.com/theskumar/python-dotenv)

---

## 7. File Structure Summary
- `app.py` — Main CLI logic and core orchestration
- `app.yaml` — Configuration (models, storage, prompt)
- `.env` — Secrets (LLM_API_KEY, etc)
- `ARCHITECTURE.md` — (This file)

---

_For questions, extensions, or in-depth explanations, see code comments or contact the maintainer._

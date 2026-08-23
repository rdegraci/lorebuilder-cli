"""Tests for bootstrap.initialize_app."""
from unittest.mock import MagicMock

import pytest

import bootstrap
import lore


def test_initialize_app_returns_context(tmp_path, monkeypatch, capture_rprint):
    capture, _ = capture_rprint
    capture(bootstrap)
    monkeypatch.chdir(tmp_path)

    (tmp_path / ".env").write_text("LLM_API_KEY=test-key\n")
    (tmp_path / "app.yaml").write_text(
        "\n".join(
            [
                "chromadb_path: ./test-chroma",
                "embedding_model: all-MiniLM-L6-v2",
                "llm_provider: openai/gpt-4o-mini",
                "chat_prompt_template: You are {character_name}.",
            ]
        )
    )

    mock_collection = MagicMock()
    mock_collection.get.return_value = {"documents": ["Mara lives in Ardelune."]}
    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_collection

    monkeypatch.setattr(
        bootstrap.chromadb,
        "PersistentClient",
        lambda path: mock_client,
    )
    monkeypatch.setattr(
        bootstrap.embedding_functions,
        "SentenceTransformerEmbeddingFunction",
        lambda model_name: MagicMock(),
    )
    monkeypatch.setattr(bootstrap.chat_history, "initialize_db", lambda: None)
    monkeypatch.setattr(
        bootstrap,
        "extract_character_names_from_lore",
        lambda docs: {"Mara"},
    )

    context = bootstrap.initialize_app()

    assert context["config"]["chromadb_path"] == "./test-chroma"
    assert context["characters_in_lore"] == {"Mara"}
    assert context["chroma_collection"] is mock_collection
    assert context["last_generated_lore"] == ""
    assert lore._lore_service is not None

    lore._lore_service = None


def test_initialize_app_raises_when_api_key_missing(tmp_path, monkeypatch, capture_rprint):
    capture, _ = capture_rprint
    capture(bootstrap)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("LLM_API_KEY", "your-model-api-key-here")
    monkeypatch.setattr(bootstrap, "load_dotenv", lambda: None)

    (tmp_path / "app.yaml").write_text(
        "chromadb_path: ./test-chroma\nembedding_model: all-MiniLM-L6-v2\n"
    )

    with pytest.raises(EnvironmentError, match="LLM_API_KEY not set"):
        bootstrap.initialize_app()


def test_initialize_app_continues_when_character_extraction_fails(
    tmp_path, monkeypatch, capture_rprint
):
    capture, buffer = capture_rprint
    capture(bootstrap)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setattr(bootstrap, "load_dotenv", lambda: None)

    (tmp_path / "app.yaml").write_text(
        "chromadb_path: ./test-chroma\nembedding_model: all-MiniLM-L6-v2\n"
    )

    mock_collection = MagicMock()
    mock_collection.get.return_value = {"documents": []}
    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_collection

    monkeypatch.setattr(
        bootstrap.chromadb,
        "PersistentClient",
        lambda path: mock_client,
    )
    monkeypatch.setattr(
        bootstrap.embedding_functions,
        "SentenceTransformerEmbeddingFunction",
        lambda model_name: MagicMock(),
    )
    monkeypatch.setattr(bootstrap.chat_history, "initialize_db", lambda: None)
    monkeypatch.setattr(
        bootstrap,
        "extract_character_names_from_lore",
        lambda docs: (_ for _ in ()).throw(RuntimeError("spaCy unavailable")),
    )

    context = bootstrap.initialize_app()

    assert context["characters_in_lore"] == set()
    assert "Could not extract character names" in buffer.getvalue()

    lore._lore_service = None

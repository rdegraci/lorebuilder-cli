"""Shared pytest fixtures for LoreBuilder CLI tests."""
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from io import StringIO
from rich.console import Console

from chat_history import ChatHistoryService
from lore import LoreService


@pytest.fixture
def capture_rprint(monkeypatch):
    """Capture Rich console output from modules that use `rprint`."""
    buffer = StringIO()
    console = Console(
        file=buffer,
        width=120,
        force_terminal=False,
        color_system=None,
        no_color=True,
        highlight=False,
    )

    def _capture(module):
        monkeypatch.setattr(module, "rprint", console.print)
        return buffer

    return _capture, buffer


@pytest.fixture
def chat_service(tmp_path):
    """ChatHistoryService backed by a temporary SQLite database."""
    service = ChatHistoryService(db_file=str(tmp_path / "test_chat.db"))
    service.initialize_db()
    return service


@pytest.fixture
def lore_context():
    """LoreService with mocked ChromaDB collection and embedder."""
    mock_collection = MagicMock()
    mock_collection.query.return_value = {"documents": [["Existing council lore"]]}
    mock_collection.get.return_value = {"documents": [], "ids": []}

    service = LoreService(
        config={
            "lore_llm_model": "openai/gpt-4o-mini",
            "prompt_template": "You are a worldbuilder. Context: {context}",
        },
        chroma_collection=mock_collection,
        embedder=lambda texts: [[0.1, 0.2] for _ in texts],
        llm_api_key="test-key",
        chat_history=None,
    )
    return {
        "service": service,
        "collection": mock_collection,
        "context": {},
    }


@pytest.fixture
def initialized_lore(lore_context):
    """Register a LoreService instance on the lore module global."""
    import lore as lore_module

    lore_module._lore_service = lore_context["service"]
    yield lore_context
    lore_module._lore_service = None


@pytest.fixture
def mock_llm_response():
    """Minimal LiteLLM-style completion response."""
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content="Generated festival lore.")
            )
        ]
    )


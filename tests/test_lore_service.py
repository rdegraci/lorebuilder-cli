"""Tests for LoreService and lore module handlers."""
import lore
import litellm
from constants import INFO_GENERATED_LORE_NOT_SAVED, WARNING_NO_LORE_TO_STORE


def test_add_lore_stores_entry_and_updates_context(lore_context, capture_rprint):
    capture, buffer = capture_rprint
    capture(lore)
    service = lore_context["service"]
    collection = lore_context["collection"]
    context = lore_context["context"]

    service.add_lore(["Mara guards the Crystal Lake."], context)

    collection.add.assert_called_once()
    assert context["last_generated_lore"] == "Mara guards the Crystal Lake."
    assert "Lore added with id" in buffer.getvalue()


def test_generate_lore_calls_llm_and_shows_store_reminder(
    lore_context, capture_rprint, mock_llm_response, monkeypatch
):
    capture, buffer = capture_rprint
    capture(lore)
    service = lore_context["service"]
    context = lore_context["context"]

    monkeypatch.setattr(litellm, "completion", lambda **kwargs: mock_llm_response)

    service.generate_lore(["Describe a festival"], context)

    assert context["last_generated_lore"] == "Generated festival lore."
    output = buffer.getvalue()
    assert "Generated Lore" in output
    assert INFO_GENERATED_LORE_NOT_SAVED.strip("[]") in output or "store_generated_lore" in output


def test_generate_lore_uses_existing_lore_context(
    lore_context, mock_llm_response, monkeypatch
):
    service = lore_context["service"]
    captured = {}

    def fake_completion(**kwargs):
        captured["messages"] = kwargs["messages"]
        return mock_llm_response

    monkeypatch.setattr(litellm, "completion", fake_completion)

    service.generate_lore(["Describe the council"], context={})

    system_prompt = captured["messages"][0]["content"]
    assert "Existing council lore" in system_prompt


def test_store_generated_lore_persists_last_generated_text(lore_context, capture_rprint):
    capture, buffer = capture_rprint
    capture(lore)
    service = lore_context["service"]
    collection = lore_context["collection"]
    context = {"last_generated_lore": "Generated festival lore."}

    service.store_generated_lore([], context)

    collection.add.assert_called_once()
    assert "Stored generated lore with id" in buffer.getvalue()


def test_store_generated_lore_warns_when_nothing_to_store(lore_context, capture_rprint):
    capture, buffer = capture_rprint
    capture(lore)
    service = lore_context["service"]

    service.store_generated_lore([], {})

    assert WARNING_NO_LORE_TO_STORE.strip("[]") in buffer.getvalue() or "No generated lore" in buffer.getvalue()


def test_query_lore_internal_returns_documents(lore_context):
    service = lore_context["service"]
    collection = lore_context["collection"]
    collection.query.return_value = {"documents": [["Council lore", "Lake lore"]]}

    docs = service.query_lore_internal("council", 2)

    assert docs == ["Council lore", "Lake lore"]
    collection.query.assert_called_once_with(query_texts=["council"], n_results=2)


def test_query_lore_prints_results(lore_context, capture_rprint):
    capture, buffer = capture_rprint
    capture(lore)
    service = lore_context["service"]
    service.chroma_collection.query.return_value = {
        "documents": [["Council lore"]]
    }

    service.query_lore(["council"], {})

    assert "Relevant Lore Entries" in buffer.getvalue()
    assert "Council lore" in buffer.getvalue()


def test_delete_lore_removes_entry(lore_context, capture_rprint):
    capture, buffer = capture_rprint
    capture(lore)
    service = lore_context["service"]
    collection = lore_context["collection"]

    service.delete_lore(["123456"], {})

    collection.delete.assert_called_once_with(ids=["123456"])
    assert "Deleted lore entry with ID 123456" in buffer.getvalue()


def test_module_handlers_require_initialized_service(capture_rprint):
    capture, buffer = capture_rprint
    capture(lore)
    lore._lore_service = None

    lore.generate_lore(["prompt"], {})

    assert "Lore service not initialized" in buffer.getvalue()


def test_init_lore_registers_global_service(lore_context):
    service = lore_context["service"]
    collection = lore_context["collection"]

    lore.init_lore(
        config=service.config,
        chroma_collection=collection,
        embedder=service.embedder,
        llm_api_key=service.llm_api_key,
        chat_history=None,
    )

    assert lore._lore_service is not None
    assert lore._lore_service.config == service.config
    assert lore._lore_service.chroma_collection is collection

    lore._lore_service = None

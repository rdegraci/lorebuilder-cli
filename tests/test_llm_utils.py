"""Tests for LiteLLM response helpers."""
from types import SimpleNamespace

from llm_utils import extract_completion_text


def test_extract_completion_text_from_attributes():
    response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content="Generated lore text")
            )
        ]
    )
    assert extract_completion_text(response) == "Generated lore text"


def test_extract_completion_text_from_dict_message():
    response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message={"content": "Dict-style message"}
            )
        ]
    )
    assert extract_completion_text(response) == "Dict-style message"


def test_extract_completion_text_returns_empty_string_when_missing():
    response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content=None)
            )
        ]
    )
    assert extract_completion_text(response) == ""

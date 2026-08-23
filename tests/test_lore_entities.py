"""Tests for lore entity extraction."""
from unittest.mock import MagicMock

import pytest

import lore_entities
from lore_entities import ensure_spacy, extract_character_names_from_lore


@pytest.fixture(autouse=True)
def reset_spacy_model():
    lore_entities.nlp = None
    yield
    lore_entities.nlp = None


def _make_doc(entities):
    doc = MagicMock()
    doc.ents = entities
    return doc


def test_extract_character_names_from_lore(monkeypatch):
    mara = MagicMock()
    mara.label_ = "PERSON"
    mara.text = "Mara"
    arin = MagicMock()
    arin.label_ = "PERSON"
    arin.text = "Arin"
    place = MagicMock()
    place.label_ = "GPE"
    place.text = "Ardelune"

    monkeypatch.setattr(
        lore_entities,
        "nlp",
        lambda text: _make_doc([mara, place, arin]),
    )

    names = extract_character_names_from_lore(
        [
            "Mara and Arin live in Ardelune.",
            "Mara guards the Crystal Lake.",
        ]
    )

    assert names == {"Mara", "Arin"}


def test_extract_character_names_deduplicates_names(monkeypatch):
    mara = MagicMock()
    mara.label_ = "PERSON"
    mara.text = "Mara"

    monkeypatch.setattr(
        lore_entities,
        "nlp",
        lambda text: _make_doc([mara]),
    )

    names = extract_character_names_from_lore(["Mara appears twice.", "Mara again."])

    assert names == {"Mara"}


def test_ensure_spacy_raises_when_model_missing(monkeypatch):
    monkeypatch.setitem(
        __import__("sys").modules,
        "en_core_web_sm",
        None,
    )

    def fake_import(name, *args, **kwargs):
        if name == "en_core_web_sm":
            raise ImportError("missing model")
        return __import__(name, *args, **kwargs)

    monkeypatch.setattr(lore_entities, "nlp", None)

    with pytest.raises(RuntimeError, match="en_core_web_sm"):
        ensure_spacy()


def test_ensure_spacy_loads_model_once(monkeypatch):
    mock_nlp = MagicMock()
    mock_module = MagicMock()
    mock_module.load.return_value = mock_nlp

    monkeypatch.setitem(__import__("sys").modules, "en_core_web_sm", mock_module)
    monkeypatch.setattr(lore_entities, "nlp", None)

    ensure_spacy()
    ensure_spacy()

    mock_module.load.assert_called_once()
    assert lore_entities.nlp is mock_nlp

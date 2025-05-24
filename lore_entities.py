"""
lore_entities.py

Utility for extracting person/character names from all saved lore using spaCy NER.
"""
import spacy
from typing import List, Set

nlp = None

def ensure_spacy():
    """
    Lazy-load spaCy model.
    """
    global nlp
    if nlp is None:
        try:
            import en_core_web_sm
            nlp = en_core_web_sm.load()
        except ImportError:
            raise RuntimeError("spaCy model 'en_core_web_sm' is not installed. Run: python -m spacy download en_core_web_sm")


def extract_character_names_from_lore(lore_entries: List[str]) -> Set[str]:
    """
    Extracts character/person names from all lore strings using spaCy NER.
    Args:
        lore_entries: List of saved lore text entries.
    Returns:
        Set of unique person/character names mentioned.
    """
    ensure_spacy()
    names = set()
    for text in lore_entries:
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                # Only store name stripped for duplicates
                names.add(ent.text.strip())
    return names

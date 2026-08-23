"""
llm_utils.py - Helpers for working with LiteLLM responses.
"""


def extract_completion_text(response) -> str:
    """
    Return assistant text from a LiteLLM completion response.

    Uses attribute access to avoid Pydantic serialization warnings that can
    occur when indexing ModelResponse objects like dictionaries.
    """
    message = response.choices[0].message
    content = getattr(message, "content", None)
    if content is not None:
        return content
    if isinstance(message, dict):
        return message.get("content", "")
    return ""

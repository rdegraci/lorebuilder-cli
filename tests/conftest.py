"""Shared pytest fixtures for LoreBuilder CLI tests."""
import pytest
from io import StringIO
from rich.console import Console


@pytest.fixture
def capture_rprint(monkeypatch):
    """Capture Rich console output from modules that use `rprint`."""
    buffer = StringIO()
    console = Console(file=buffer, width=120, force_terminal=True)

    def _capture(module):
        monkeypatch.setattr(module, "rprint", console.print)
        return buffer

    return _capture, buffer

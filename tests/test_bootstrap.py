"""Tests for bootstrap config file setup."""
import bootstrap
from constants import CONFIG_FILE, ENV_FILE


def test_ensure_env_file_creates_from_example(tmp_path, monkeypatch, capture_rprint):
    capture, _ = capture_rprint
    capture(bootstrap)
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env.example").write_text("LLM_API_KEY=from-example\n")

    bootstrap._ensure_env_file()

    assert (tmp_path / ENV_FILE).read_text() == "LLM_API_KEY=from-example\n"


def test_ensure_env_file_uses_fallback_when_example_missing(tmp_path, monkeypatch, capture_rprint):
    capture, _ = capture_rprint
    capture(bootstrap)
    monkeypatch.chdir(tmp_path)

    bootstrap._ensure_env_file()

    assert "LLM_API_KEY=your-model-api-key-here" in (tmp_path / ENV_FILE).read_text()


def test_ensure_env_file_does_not_overwrite_existing(tmp_path, monkeypatch, capture_rprint):
    capture, _ = capture_rprint
    capture(bootstrap)
    monkeypatch.chdir(tmp_path)
    (tmp_path / ENV_FILE).write_text("LLM_API_KEY=existing\n")

    bootstrap._ensure_env_file()

    assert (tmp_path / ENV_FILE).read_text() == "LLM_API_KEY=existing\n"


def test_ensure_config_file_creates_from_example(tmp_path, monkeypatch, capture_rprint):
    capture, _ = capture_rprint
    capture(bootstrap)
    monkeypatch.chdir(tmp_path)
    (tmp_path / "app.yaml.example").write_text("chromadb_path: ./test-chroma\n")

    bootstrap._ensure_config_file()

    assert (tmp_path / CONFIG_FILE).read_text() == "chromadb_path: ./test-chroma\n"


def test_ensure_config_file_uses_fallback_when_example_missing(tmp_path, monkeypatch, capture_rprint):
    capture, _ = capture_rprint
    capture(bootstrap)
    monkeypatch.chdir(tmp_path)

    bootstrap._ensure_config_file()

    content = (tmp_path / CONFIG_FILE).read_text()
    assert "chromadb_path: ./chromadb" in content
    assert "embedding_model: all-MiniLM-L6-v2" in content


def test_ensure_config_file_does_not_overwrite_existing(tmp_path, monkeypatch, capture_rprint):
    capture, _ = capture_rprint
    capture(bootstrap)
    monkeypatch.chdir(tmp_path)
    (tmp_path / CONFIG_FILE).write_text("chromadb_path: ./existing\n")

    bootstrap._ensure_config_file()

    assert (tmp_path / CONFIG_FILE).read_text() == "chromadb_path: ./existing\n"

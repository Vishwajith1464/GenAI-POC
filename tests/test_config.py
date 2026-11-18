import pytest
from pydantic import ValidationError

from research_agent.config import Settings


def test_loads_values_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test_key")
    monkeypatch.setenv("GEMINI_MODEL_NAME", "test_model")

    settings = Settings(_env_file=None)
    assert settings.gemini_api_key.get_secret_value() == "test_key"
    assert settings.gemini_model_name == "test_model"


def test_missing_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ValidationError, match="gemini_api_key"):
        Settings(_env_file=None)

def test_blank_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "  ")
    with pytest.raises(ValidationError, match="gemini_api_key"):
        Settings(_env_file=None)

def test_model_name_has_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GEMINI_MODEL_NAME", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "test_key")
    settings = Settings(_env_file=None)
    assert settings.gemini_model_name == "gemini-3.8-flash"

def test_key_is_masked_when_printed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "super-secret-123")
    settings = Settings(_env_file=None)
    assert "super-secret-123" not in str(settings)
    assert "super-secret-123" not in repr(settings)

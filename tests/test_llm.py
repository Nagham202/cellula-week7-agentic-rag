import pytest

import config
from src.llm import get_llm

# these only build the llm objects, nothing is sent


def test_missing_key_for_the_main_provider_is_a_clear_error(monkeypatch):
    monkeypatch.setattr(config, "LLM_PROVIDER", "groq")
    monkeypatch.setattr(config, "GROQ_API_KEY", None)
    with pytest.raises(ValueError, match="API key for groq is missing"):
        get_llm("rewriter")


def test_unknown_role_is_an_error():
    with pytest.raises(ValueError, match="Unknown role"):
        get_llm("translator")


def test_fallbacks_skip_providers_without_a_key(monkeypatch):
    monkeypatch.setattr(config, "LLM_PROVIDER", "groq")
    monkeypatch.setattr(config, "GROQ_API_KEY", "fake-key")
    monkeypatch.setattr(config, "OPENROUTER_API_KEY", None)
    llm = get_llm("rewriter")
    # openrouter has no key here, so only ollama is left as a backup
    assert [type(backup).__name__ for backup in llm.fallbacks] == ["ChatOllama"]

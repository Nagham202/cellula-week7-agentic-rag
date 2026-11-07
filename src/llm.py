from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

import config

OPENROUTER_URL = "https://openrouter.ai/api/v1"
FALLBACK_ORDER = ["groq", "openrouter", "ollama"]
# few retries, so a busy provider hands over to the next one quickly
MAX_RETRIES = 2


def make_groq(role):
    if not config.GROQ_API_KEY:
        return None
    model = config.GROQ_MODELS[role]
    reasoning_effort = None
    # only gpt-oss has the low/medium/high setting
    if model.startswith("openai/gpt-oss"):
        reasoning_effort = config.GROQ_REASONING_EFFORT
    return ChatGroq(model=model, temperature=config.LLM_TEMPERATURE, api_key=config.GROQ_API_KEY,
                    reasoning_effort=reasoning_effort, max_retries=MAX_RETRIES)


def make_openrouter(role):
    if not config.OPENROUTER_API_KEY:
        return None
    return ChatOpenAI(model=config.OPENROUTER_MODELS[role], temperature=config.LLM_TEMPERATURE,
                      api_key=config.OPENROUTER_API_KEY, base_url=OPENROUTER_URL, max_retries=MAX_RETRIES)


def make_ollama(role):
    return ChatOllama(model=config.OLLAMA_MODEL, temperature=config.LLM_TEMPERATURE)


MAKERS = {"groq": make_groq, "openrouter": make_openrouter, "ollama": make_ollama}


def get_llm(role):
    if role not in config.GROQ_MODELS:
        raise ValueError(f"Unknown role: {role}. Use one of {list(config.GROQ_MODELS)}.")
    if config.LLM_PROVIDER not in MAKERS:
        raise ValueError(f"Unknown LLM_PROVIDER: {config.LLM_PROVIDER}. Use 'groq', 'openrouter' or 'ollama'.")

    main_llm = MAKERS[config.LLM_PROVIDER](role)
    # no key for the main provider is a setup mistake, better to fail than switch silently
    if main_llm is None:
        raise ValueError(f"The API key for {config.LLM_PROVIDER} is missing. Put it in .env (see .env.example).")
    if not config.USE_FALLBACKS:
        return main_llm

    backups = []
    for provider in FALLBACK_ORDER:
        if provider == config.LLM_PROVIDER:
            continue
        backup_llm = MAKERS[provider](role)
        if backup_llm is not None:
            backups.append(backup_llm)
    return main_llm.with_fallbacks(backups)


# quick test: python -m src.llm
if __name__ == "__main__":
    import time

    for provider in FALLBACK_ORDER:
        llm = MAKERS[provider]("rewriter")
        if llm is None:
            print(f"{provider}: skipped (no API key in .env)")
            continue
        start = time.time()
        try:
            reply = llm.invoke("Reply with exactly one word: Hello")
            print(f"{provider}: {reply.content!r} in {time.time() - start:.1f} s")
        except Exception as error:
            print(f"{provider}: FAILED - {type(error).__name__}: {str(error)[:150]}")

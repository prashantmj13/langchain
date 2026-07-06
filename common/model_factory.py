"""
Single place every module gets a chat model from.

Defaults to Anthropic's Claude. Swap providers repo-wide by setting LLM_PROVIDER
in your .env (anthropic | openai | google | ollama) -- no other code changes needed.
Each module's README also shows the equivalent direct, non-factory diff for
side-by-side comparisons.
"""

import os

from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel

load_dotenv()

DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-5",
    "openai": "gpt-4o-mini",
    "google": "gemini-1.5-pro",
    "ollama": "llama3.1",
}


def get_chat_model(
    provider: str | None = None,
    model: str | None = None,
    temperature: float = 0.7,
    **kwargs,
) -> BaseChatModel:
    """Return a LangChain chat model for the requested provider.

    provider defaults to the LLM_PROVIDER env var, or "anthropic" if unset.
    """
    provider = (provider or os.getenv("LLM_PROVIDER", "anthropic")).lower()
    model = model or DEFAULT_MODELS.get(provider)

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(model=model, temperature=temperature, **kwargs)

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=model, temperature=temperature, **kwargs)

    if provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(model=model, temperature=temperature, **kwargs)

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(model=model, temperature=temperature, **kwargs)

    raise ValueError(
        f"Unknown LLM_PROVIDER '{provider}'. Expected one of: "
        f"{', '.join(DEFAULT_MODELS)}"
    )

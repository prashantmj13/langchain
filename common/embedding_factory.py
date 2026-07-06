"""
Single place every module gets an embeddings model from.

Anthropic does not ship its own embedding model; Voyage AI is Anthropic's
recommended embeddings partner (https://docs.anthropic.com/en/docs/build-with-claude/embeddings),
so it's the default here. Swap repo-wide via EMBEDDING_PROVIDER in .env
(voyage | openai | huggingface).
"""

import os

from dotenv import load_dotenv
from langchain_core.embeddings import Embeddings

load_dotenv()

DEFAULT_MODELS = {
    "voyage": "voyage-3.5",
    "openai": "text-embedding-3-small",
    "huggingface": "sentence-transformers/all-MiniLM-L6-v2",
}


def get_embeddings(provider: str | None = None, model: str | None = None, **kwargs) -> Embeddings:
    """Return a LangChain embeddings model for the requested provider.

    provider defaults to the EMBEDDING_PROVIDER env var, or "voyage" if unset.
    """
    provider = (provider or os.getenv("EMBEDDING_PROVIDER", "voyage")).lower()
    model = model or DEFAULT_MODELS.get(provider)

    if provider == "voyage":
        from langchain_voyageai import VoyageAIEmbeddings

        return VoyageAIEmbeddings(model=model, **kwargs)

    if provider == "openai":
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(model=model, **kwargs)

    if provider == "huggingface":
        from langchain_community.embeddings import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(model_name=model, **kwargs)

    raise ValueError(
        f"Unknown EMBEDDING_PROVIDER '{provider}'. Expected one of: "
        f"{', '.join(DEFAULT_MODELS)}"
    )

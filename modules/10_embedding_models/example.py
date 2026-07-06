"""
Module 10 - Embedding Models: comparing Voyage AI, OpenAI, and local HuggingFace embeddings.

Run: python modules/10_embedding_models/example.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from common.embedding_factory import get_embeddings

SENTENCES = [
    "LangChain makes it easy to compose LLM pipelines.",
    "Claude is a large language model built by Anthropic.",
    "The recipe calls for two cups of flour and a pinch of salt.",
]


def try_provider(provider: str):
    print(f"\n--- {provider} ---")
    try:
        embeddings_model = get_embeddings(provider=provider)
        vectors = embeddings_model.embed_documents(SENTENCES)
        print(f"Dimensionality: {len(vectors[0])}")
        print(f"First 5 values of vector 0: {vectors[0][:5]}")
    except Exception as exc:  # noqa: BLE001 - demo script, provider may not be configured
        print(f"Skipped ({exc.__class__.__name__}: {exc})")


if __name__ == "__main__":
    for provider in ("voyage", "openai", "huggingface"):
        try_provider(provider)

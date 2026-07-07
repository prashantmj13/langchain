"""
Module 10 - Exercise solutions.

Run: python modules/10_embedding_models/solutions.py
"""

import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from common.embedding_factory import get_embeddings


def exercise_1():
    """Print vector dimensionality for every configured provider."""
    print("--- Exercise 1: dimensionality ---")
    for provider in ("voyage", "openai", "huggingface"):
        try:
            vector = get_embeddings(provider=provider).embed_query("hello world")
            print(f"{provider}: {len(vector)} dims")
        except Exception as exc:  # noqa: BLE001
            print(f"{provider}: skipped ({exc.__class__.__name__})")


def exercise_2():
    """Time embed_documents() on 50 short sentences per provider."""
    sentences = [f"This is test sentence number {i}." for i in range(50)]

    print("\n--- Exercise 2: latency on 50 sentences ---")
    for provider in ("voyage", "openai", "huggingface"):
        try:
            embeddings_model = get_embeddings(provider=provider)
            start = time.perf_counter()
            embeddings_model.embed_documents(sentences)
            elapsed = time.perf_counter() - start
            print(f"{provider}: {elapsed:.2f}s")
        except Exception as exc:  # noqa: BLE001
            print(f"{provider}: skipped ({exc.__class__.__name__})")


def exercise_3():
    """Compare voyage-code-3 vs. the general-purpose model on code snippets."""
    snippets = [
        "def add(a, b):\n    return a + b",
        "SELECT * FROM users WHERE active = true;",
        "const sum = (a, b) => a + b;",
    ]

    print("\n--- Exercise 3: code-specialized vs. general embeddings ---")
    try:
        general = get_embeddings(provider="voyage")
        code_specific = get_embeddings(provider="voyage", model="voyage-code-3")

        general_vectors = general.embed_documents(snippets)
        code_vectors = code_specific.embed_documents(snippets)
        print(f"General model dims: {len(general_vectors[0])}, code model dims: {len(code_vectors[0])}")
        print("(Compare similarity rankings between the two on a larger code corpus for a real signal.)")
    except Exception as exc:  # noqa: BLE001
        print(f"Skipped ({exc.__class__.__name__}: {exc})")


def exercise_4():
    """Confirm embed_query(text) == embed_documents([text])[0]."""
    embeddings_model = get_embeddings()
    text = "LangChain is a framework for LLM applications."

    query_vector = embeddings_model.embed_query(text)
    doc_vector = embeddings_model.embed_documents([text])[0]

    print("\n--- Exercise 4: embed_query vs embed_documents ---")
    print("Same length:", len(query_vector) == len(doc_vector))
    print("Numerically equal (first 5 values):", query_vector[:5] == doc_vector[:5])


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()

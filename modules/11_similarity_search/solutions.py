"""
Module 11 - Exercise solutions.

Run: python modules/11_similarity_search/solutions.py
"""

import sys
import time
from pathlib import Path

import numpy as np

sys.path.append(str(Path(__file__).resolve().parents[2]))

from common.embedding_factory import get_embeddings

DOCUMENTS = [
    "You can reset your password from the account settings page.",
    "Our return policy allows returns within 30 days of purchase.",
    "Standard shipping takes 5-7 business days within the US.",
    "You can upgrade or downgrade your subscription plan at any time.",
    "We accept Visa, Mastercard, and PayPal for payment.",
    "International orders may be subject to customs fees.",
    "You can cancel your subscription anytime from the billing page.",
]


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def euclidean_distance(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b))


def exercise_1():
    """Add a 7th document (already added to DOCUMENTS above), test 3 queries."""
    embeddings_model = get_embeddings()
    doc_vectors = [np.array(v) for v in embeddings_model.embed_documents(DOCUMENTS)]

    print("--- Exercise 1: 7-document corpus, 3 queries ---")
    for query in ["How do I stop being billed?", "What countries can I ship to?", "How do I change my plan?"]:
        query_vector = np.array(embeddings_model.embed_query(query))
        scored = sorted(
            zip(DOCUMENTS, doc_vectors),
            key=lambda pair: cosine_similarity(query_vector, pair[1]),
            reverse=True,
        )
        print(f"\nQuery: {query!r}")
        for doc, _ in scored[:2]:
            print("  -", doc)


def exercise_2():
    """Rank by Euclidean distance too, compare top-3 ordering to cosine similarity."""
    embeddings_model = get_embeddings()
    doc_vectors = [np.array(v) for v in embeddings_model.embed_documents(DOCUMENTS)]
    query_vector = np.array(embeddings_model.embed_query("How do I get my money back?"))

    cosine_ranked = sorted(
        zip(DOCUMENTS, doc_vectors), key=lambda p: cosine_similarity(query_vector, p[1]), reverse=True
    )
    euclidean_ranked = sorted(
        zip(DOCUMENTS, doc_vectors), key=lambda p: euclidean_distance(query_vector, p[1])
    )

    print("\n--- Exercise 2: cosine vs euclidean top-3 ---")
    print("Cosine top-3:   ", [d for d, _ in cosine_ranked[:3]])
    print("Euclidean top-3:", [d for d, _ in euclidean_ranked[:3]])


def exercise_3():
    """Add a similarity-score threshold; test a query that should return zero matches."""
    embeddings_model = get_embeddings()
    doc_vectors = [np.array(v) for v in embeddings_model.embed_documents(DOCUMENTS)]
    threshold = 0.5

    def search(query: str):
        query_vector = np.array(embeddings_model.embed_query(query))
        scored = [(doc, cosine_similarity(query_vector, v)) for doc, v in zip(DOCUMENTS, doc_vectors)]
        return [(doc, score) for doc, score in scored if score >= threshold]

    print("\n--- Exercise 3: threshold-filtered search ---")
    unrelated_query = "What is the airspeed velocity of an unladen swallow?"
    results = search(unrelated_query)
    print(f"Query: {unrelated_query!r}")
    print(f"Results above threshold {threshold}: {len(results)}")


def exercise_4():
    """Benchmark brute-force search against 10,000 random vectors."""
    rng = np.random.default_rng(42)
    corpus = rng.random((10_000, 384))
    query = rng.random(384)

    start = time.perf_counter()
    norms = np.linalg.norm(corpus, axis=1)
    scores = corpus @ query / (norms * np.linalg.norm(query))
    top_5 = np.argsort(scores)[-5:]
    elapsed = time.perf_counter() - start

    print("\n--- Exercise 4: brute-force search over 10,000 vectors ---")
    print(f"Search took {elapsed * 1000:.2f}ms, top indices: {top_5}")
    print("(Compare this to the 7-document demo above -- brute-force scales linearly with corpus size.)")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()

"""
Module 11 - Similarity Search: manual top-k ranking with cosine similarity.

Run: python modules/11_similarity_search/example.py
"""

import sys
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
]


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def top_k(query: str, k: int = 3):
    embeddings_model = get_embeddings()
    doc_vectors = [np.array(v) for v in embeddings_model.embed_documents(DOCUMENTS)]
    query_vector = np.array(embeddings_model.embed_query(query))

    scored = [
        (doc, cosine_similarity(query_vector, doc_vector))
        for doc, doc_vector in zip(DOCUMENTS, doc_vectors)
    ]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:k]


if __name__ == "__main__":
    for query in ["How do I get my money back?", "What payment methods work here?"]:
        print(f"\nQuery: {query!r}")
        for doc, score in top_k(query):
            print(f"  {score:.3f}  {doc}")

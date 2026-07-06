"""
Module 09 - Embeddings Theory: cosine similarity from first principles, then with real embeddings.

Run: python modules/09_embeddings_theory/example.py
"""

import sys
from pathlib import Path

import numpy as np

sys.path.append(str(Path(__file__).resolve().parents[2]))

from common.embedding_factory import get_embeddings


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def toy_vector_demo():
    print("--- Toy vectors (no API call) ---")
    vectors = {
        "king": np.array([0.9, 0.8, 0.1]),
        "queen": np.array([0.85, 0.75, 0.6]),
        "apple": np.array([0.1, 0.05, 0.9]),
    }
    pairs = [("king", "queen"), ("king", "apple"), ("queen", "apple")]
    for a, b in pairs:
        sim = cosine_similarity(vectors[a], vectors[b])
        print(f"cosine({a}, {b}) = {sim:.3f}")


def real_embedding_demo():
    print("\n--- Real embeddings ---")
    sentences = [
        "The cat sat on the mat.",
        "A kitten was resting on the rug.",
        "The stock market fell sharply today.",
        "Tech stocks dropped after the earnings report.",
    ]
    embeddings_model = get_embeddings()
    vectors = [np.array(v) for v in embeddings_model.embed_documents(sentences)]

    print("\nPairwise cosine similarity matrix:")
    header = "                                   " + "".join(f"S{i+1:<8}" for i in range(len(sentences)))
    print(header)
    for i, vi in enumerate(vectors):
        row = f"S{i+1} {sentences[i][:30]:<30}"
        for vj in vectors:
            row += f"{cosine_similarity(vi, vj):<9.3f}"
        print(row)


if __name__ == "__main__":
    toy_vector_demo()
    real_embedding_demo()

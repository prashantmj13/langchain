"""
Module 09 - Exercise solutions.

Run: python modules/09_embeddings_theory/solutions.py
"""

import sys
from pathlib import Path

import numpy as np

sys.path.append(str(Path(__file__).resolve().parents[2]))

from common.embedding_factory import get_embeddings


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def exercise_1():
    """By hand: cosine similarity between [1, 0] and [0, 1]."""
    a, b = np.array([1, 0]), np.array([0, 1])
    sim = cosine_similarity(a, b)
    print("--- Exercise 1 ---")
    print(f"cosine([1,0], [0,1]) = {sim}")
    print("It's 0 because the vectors are orthogonal (perpendicular): their dot")
    print("product (1*0 + 0*1 = 0) is zero, and cosine similarity is proportional")
    print("to the dot product -- zero dot product means zero similarity.")


def exercise_2():
    """A scaled copy of a vector has identical cosine similarity (magnitude-invariant)."""
    v1 = np.array([0.9, 0.8, 0.1])
    v1_scaled = 2 * v1

    print("\n--- Exercise 2 ---")
    print("cosine(v1, v1)       =", cosine_similarity(v1, v1))
    print("cosine(v1, 2*v1)     =", cosine_similarity(v1, v1_scaled))
    print("Identical, because cosine similarity normalizes by vector magnitude.")


def exercise_3():
    """6 sentences (3 sports, 3 cooking): same-topic pairs should score higher."""
    sentences = [
        "The team won the championship game last night.",  # sports
        "She scored the winning goal in overtime.",  # sports
        "The coach called a timeout in the final minute.",  # sports
        "Add two cups of flour and a pinch of salt.",  # cooking
        "Simmer the sauce for twenty minutes on low heat.",  # cooking
        "Whisk the eggs until they are light and fluffy.",  # cooking
    ]
    embeddings_model = get_embeddings()
    vectors = [np.array(v) for v in embeddings_model.embed_documents(sentences)]

    same_topic = cosine_similarity(vectors[0], vectors[1])  # sports vs sports
    cross_topic = cosine_similarity(vectors[0], vectors[3])  # sports vs cooking

    print("\n--- Exercise 3 ---")
    print(f"Same-topic similarity (sports, sports): {same_topic:.3f}")
    print(f"Cross-topic similarity (sports, cooking): {cross_topic:.3f}")
    print("Same-topic should score higher:", same_topic > cross_topic)


def exercise_4():
    """Truncate an embedding to its first 256 dims, compare ranking before/after."""
    sentences = [
        "The cat sat on the mat.",
        "A kitten was resting on the rug.",
        "The stock market fell sharply today.",
    ]
    embeddings_model = get_embeddings()
    vectors = [np.array(v) for v in embeddings_model.embed_documents(sentences)]

    dim = len(vectors[0])
    truncate_to = min(256, dim)

    full_sim = cosine_similarity(vectors[0], vectors[1])
    truncated_sim = cosine_similarity(vectors[0][:truncate_to], vectors[1][:truncate_to])

    print("\n--- Exercise 4 ---")
    print(f"Full dimensionality: {dim}")
    print(f"Full-vector similarity (sentence 0 vs 1):      {full_sim:.4f}")
    print(f"Truncated-to-{truncate_to} similarity (same pair): {truncated_sim:.4f}")
    print("Ranking is usually preserved closely, though the exact score shifts.")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()

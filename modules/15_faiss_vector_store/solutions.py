"""
Module 15 - Exercise solutions.

Run: python modules/15_faiss_vector_store/solutions.py
"""

import shutil
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from common.embedding_factory import get_embeddings

INDEX_DIR = Path(__file__).resolve().parent / "faiss_index_solutions"

DOCUMENTS = [
    Document(page_content="FAISS is a library for efficient similarity search of dense vectors.", metadata={"id": "d1"}),
    Document(page_content="FAISS indexes are saved locally as index.faiss and index.pkl.", metadata={"id": "d2"}),
    Document(page_content="IndexFlatL2 performs exact search; IVF/HNSW trade accuracy for speed.", metadata={"id": "d3"}),
]


def exercise_1():
    """Delete the on-disk index and confirm it rebuilds cleanly from scratch."""
    if INDEX_DIR.exists():
        shutil.rmtree(INDEX_DIR)
    print("--- Exercise 1: rebuild from scratch ---")
    print(f"Confirmed {INDEX_DIR} does not exist:", not INDEX_DIR.exists())

    store = FAISS.from_documents(DOCUMENTS, embedding=get_embeddings(), ids=["d1", "d2", "d3"])
    store.save_local(str(INDEX_DIR))
    print(f"Rebuilt and saved to {INDEX_DIR}")
    return store


def exercise_2():
    """Delete a document by id, confirm it no longer appears after re-saving/reloading."""
    embeddings_model = get_embeddings()
    store = FAISS.from_documents(DOCUMENTS, embedding=embeddings_model, ids=["d1", "d2", "d3"])

    store.delete(ids=["d2"])
    store.save_local(str(INDEX_DIR))

    reloaded = FAISS.load_local(str(INDEX_DIR), embeddings_model, allow_dangerous_deserialization=True)
    results = reloaded.similarity_search("How does FAISS persist data to disk?", k=3)

    print("\n--- Exercise 2: delete by id ---")
    print("Remaining documents:", [doc.metadata.get("id") for doc in results])
    print("'d2' should be absent.")


def exercise_3():
    """Loading an index with a different embedding provider than the one that built it."""
    embeddings_a = get_embeddings(provider="voyage")
    store = FAISS.from_documents(DOCUMENTS, embedding=embeddings_a)
    store.save_local(str(INDEX_DIR))

    print("\n--- Exercise 3: mismatched embedding provider ---")
    try:
        embeddings_b = get_embeddings(provider="huggingface")
        mismatched_store = FAISS.load_local(str(INDEX_DIR), embeddings_b, allow_dangerous_deserialization=True)
        results = mismatched_store.similarity_search("FAISS persistence", k=1)
        print("Loaded without error, but results are likely nonsensical because the query")
        print("vector space (huggingface) doesn't match the index's vector space (voyage):")
        print(results)
    except Exception as exc:  # noqa: BLE001
        print(f"Failed as expected: {exc.__class__.__name__}: {exc}")


def exercise_4():
    """Build an index from 5,000 synthetic strings, measure search latency."""
    from langchain_core.embeddings import DeterministicFakeEmbedding

    # A fake, dependency-free embedding model so this exercise runs instantly without API calls.
    fake_embeddings = DeterministicFakeEmbedding(size=384)
    synthetic_docs = [Document(page_content=f"Synthetic document number {i} about topic {i % 20}.") for i in range(5000)]

    start = time.perf_counter()
    large_store = FAISS.from_documents(synthetic_docs, embedding=fake_embeddings)
    build_time = time.perf_counter() - start

    start = time.perf_counter()
    large_store.similarity_search("topic 5", k=3)
    search_time = time.perf_counter() - start

    print("\n--- Exercise 4: 5,000-document index ---")
    print(f"Build time: {build_time:.2f}s")
    print(f"Search time: {search_time * 1000:.2f}ms (compare to the 3-document demo index)")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()

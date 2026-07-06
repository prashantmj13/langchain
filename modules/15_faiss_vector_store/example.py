"""
Module 15 - FAISS Vector Store: build, save, reload, and update a local index.

Run: python modules/15_faiss_vector_store/example.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from common.embedding_factory import get_embeddings

INDEX_DIR = Path(__file__).resolve().parent / "faiss_index"

DOCUMENTS = [
    Document(page_content="FAISS is a library for efficient similarity search of dense vectors."),
    Document(page_content="FAISS indexes are saved locally as a pair of files: index.faiss and index.pkl."),
    Document(page_content="IndexFlatL2 performs exact search; IVF and HNSW trade accuracy for speed at scale."),
]


def build_and_save():
    embeddings_model = get_embeddings()
    store = FAISS.from_documents(DOCUMENTS, embedding=embeddings_model)
    store.save_local(str(INDEX_DIR))
    print(f"Saved FAISS index to {INDEX_DIR}")
    return store


def load_from_disk():
    embeddings_model = get_embeddings()
    store = FAISS.load_local(str(INDEX_DIR), embeddings_model, allow_dangerous_deserialization=True)
    print(f"Loaded FAISS index from {INDEX_DIR} (no re-embedding needed)")
    return store


if __name__ == "__main__":
    build_and_save()

    reloaded_store = load_from_disk()
    print("\n--- Search on reloaded index ---")
    for doc in reloaded_store.similarity_search("How does FAISS persist data?", k=2):
        print("-", doc.page_content)

    reloaded_store.add_documents([Document(page_content="HNSW builds a graph structure for fast approximate search.")])
    reloaded_store.save_local(str(INDEX_DIR))
    print("\nAdded a new document and re-saved the index.")

    print("\n--- Search after update ---")
    for doc in reloaded_store.similarity_search("graph based approximate search", k=1):
        print("-", doc.page_content)

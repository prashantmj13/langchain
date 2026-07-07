"""
Module 12 - Exercise solutions.

Run: python modules/12_vector_stores/solutions.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_chroma import Chroma
from langchain_core.documents import Document

from common.embedding_factory import get_embeddings

DOCUMENTS = [
    Document(page_content="You can reset your password from account settings.", metadata={"category": "account"}),
    Document(page_content="Reset your password by clicking 'Forgot password' on login.", metadata={"category": "account"}),
    Document(page_content="Returns are accepted within 30 days with a receipt.", metadata={"category": "billing"}),
    Document(page_content="Refunds are processed within 5-7 business days.", metadata={"category": "billing"}),
    Document(page_content="Standard shipping takes 5-7 business days.", metadata={"category": "shipping"}),
]

PERSIST_DIR = Path(__file__).resolve().parent / "chroma_db_demo"


def exercise_1():
    """Metadata filter: search only within category == 'billing'."""
    store = Chroma.from_documents(DOCUMENTS, embedding=get_embeddings(), collection_name="ex1")
    print("--- Exercise 1: metadata filter ---")
    for doc in store.similarity_search("How long until I get my money back?", k=2, filter={"category": "billing"}):
        print("-", doc.page_content, doc.metadata)


def exercise_2():
    """Compare similarity_search vs MMR on near-duplicate documents."""
    near_duplicates = [
        Document(page_content="Password reset instructions are on the login page."),
        Document(page_content="You can reset your password from the login screen."),
        Document(page_content="To reset your password, go to the login page and click reset."),
        Document(page_content="Shipping takes 5-7 business days."),
    ]
    store = Chroma.from_documents(near_duplicates, embedding=get_embeddings(), collection_name="ex2")

    print("\n--- Exercise 2: similarity_search vs MMR (redundancy) ---")
    print("similarity_search:")
    for doc in store.similarity_search("how do I reset my password", k=3):
        print("  -", doc.page_content)

    print("max_marginal_relevance_search:")
    for doc in store.max_marginal_relevance_search("how do I reset my password", k=3, fetch_k=4):
        print("  -", doc.page_content)


def exercise_3():
    """Persist Chroma to disk, then reload it in a fresh Chroma() call."""
    embeddings_model = get_embeddings()
    store = Chroma.from_documents(
        DOCUMENTS, embedding=embeddings_model, collection_name="ex3", persist_directory=str(PERSIST_DIR)
    )
    print(f"\n--- Exercise 3: persisted to {PERSIST_DIR} ---")

    # Simulate a fresh process: a brand new Chroma() pointed at the same directory/collection.
    reloaded_store = Chroma(
        collection_name="ex3", embedding_function=embeddings_model, persist_directory=str(PERSIST_DIR)
    )
    results = reloaded_store.similarity_search("password reset", k=1)
    print("Reloaded without re-embedding, search still works:", results[0].page_content)


def exercise_4():
    """Chroma has no true 'update' -- delete + re-add is required."""
    store = Chroma.from_documents(DOCUMENTS, embedding=get_embeddings(), collection_name="ex4", ids=["doc-1"] + [f"auto-{i}" for i in range(len(DOCUMENTS) - 1)])

    print("\n--- Exercise 4: delete + re-add (no true update) ---")
    print("Before:", store.get(ids=["doc-1"])["documents"])

    store.delete(ids=["doc-1"])
    store.add_documents(
        [Document(page_content="UPDATED: reset your password via the mobile app settings screen.")],
        ids=["doc-1"],
    )
    print("After:", store.get(ids=["doc-1"])["documents"])


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()

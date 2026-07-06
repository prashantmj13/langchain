"""
Module 12 - Vector Stores: a general-purpose walkthrough using Chroma (in-memory).

Run: python modules/12_vector_stores/example.py
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


def build_store() -> Chroma:
    embeddings_model = get_embeddings()
    return Chroma.from_documents(DOCUMENTS, embedding=embeddings_model, collection_name="module12_demo")


if __name__ == "__main__":
    store = build_store()

    print("--- similarity_search ---")
    for doc in store.similarity_search("How do I get my money back?", k=2):
        print("-", doc.page_content, doc.metadata)

    print("\n--- similarity_search_with_score ---")
    for doc, score in store.similarity_search_with_score("How do I log in again?", k=2):
        print(f"- ({score:.3f}) {doc.page_content}")

    print("\n--- max_marginal_relevance_search (reduces redundancy) ---")
    for doc in store.max_marginal_relevance_search("password reset", k=2, fetch_k=4):
        print("-", doc.page_content)

    print("\n--- metadata filter (category=billing) ---")
    for doc in store.similarity_search("refund", k=2, filter={"category": "billing"}):
        print("-", doc.page_content)

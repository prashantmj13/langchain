"""
Module 14 - Retrieval: the retriever interface and create_retrieval_chain.

Run: python modules/14_retrieval/example.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

from common.embedding_factory import get_embeddings
from common.model_factory import get_chat_model

DOCUMENTS = [
    Document(page_content="LangChain retrievers implement a single invoke(query) method returning documents."),
    Document(page_content="A retriever can be backed by a vector store, a keyword index, or a hybrid of both."),
    Document(page_content="create_retrieval_chain combines a retriever with a document-combining chain."),
    Document(page_content="MMR search reduces redundancy by penalizing documents similar to already-selected ones."),
]


def build_retriever(search_type: str = "similarity", k: int = 2):
    embeddings_model = get_embeddings()
    store = Chroma.from_documents(DOCUMENTS, embedding=embeddings_model, collection_name="module14_demo")
    return store.as_retriever(search_type=search_type, search_kwargs={"k": k})


def raw_retriever_demo():
    retriever = build_retriever()
    print("--- Raw retriever.invoke() ---")
    for doc in retriever.invoke("How do I reduce duplicate results?"):
        print("-", doc.page_content)


def retrieval_chain_demo():
    retriever = build_retriever()
    llm = get_chat_model()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Answer using only the provided context. Be concise.\n\nContext:\n{context}"),
            ("human", "{input}"),
        ]
    )
    combine_docs_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)

    result = retrieval_chain.invoke({"input": "What does create_retrieval_chain do?"})
    print("\n--- create_retrieval_chain ---")
    print("Answer:", result["answer"])
    print("Context used:")
    for doc in result["context"]:
        print("  -", doc.page_content)


if __name__ == "__main__":
    raw_retriever_demo()
    retrieval_chain_demo()

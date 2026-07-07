"""
Module 14 - Exercise solutions.

Run: python modules/14_retrieval/solutions.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.retrievers.multi_query import MultiQueryRetriever
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
    Document(page_content="Retrievers are Runnables, so they compose with the LCEL pipe operator."),
    Document(page_content="A vector store's as_retriever() method is the most common way to build a retriever."),
]


def _build_store():
    return Chroma.from_documents(DOCUMENTS, embedding=get_embeddings(), collection_name="module14_solutions")


def exercise_1():
    """Compare k=2 vs k=4 retrieval on the retrieval chain's answer."""
    store = _build_store()
    llm = get_chat_model()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Answer using only the provided context. Be concise.\n\nContext:\n{context}"),
            ("human", "{input}"),
        ]
    )
    combine_docs_chain = create_stuff_documents_chain(llm, prompt)

    print("--- Exercise 1: k=2 vs k=4 ---")
    for k in (2, 4):
        retriever = store.as_retriever(search_kwargs={"k": k})
        chain = create_retrieval_chain(retriever, combine_docs_chain)
        result = chain.invoke({"input": "What is a retriever in LangChain?"})
        print(f"\nk={k} ({len(result['context'])} docs used):")
        print(result["answer"])


def exercise_2():
    """A score_threshold retriever returning zero documents for an unrelated query."""
    store = _build_store()
    retriever = store.as_retriever(
        search_type="similarity_score_threshold", search_kwargs={"k": 4, "score_threshold": 0.6}
    )

    print("\n--- Exercise 2: score_threshold ---")
    results = retriever.invoke("What's the best recipe for lasagna?")
    print(f"Documents returned for an unrelated query: {len(results)}")


def exercise_3():
    """Wrap the retriever with MultiQueryRetriever to widen recall on a vague query."""
    store = _build_store()
    base_retriever = store.as_retriever(search_kwargs={"k": 2})
    llm = get_chat_model()

    multi_query_retriever = MultiQueryRetriever.from_llm(retriever=base_retriever, llm=llm)

    vague_query = "how does LangChain find stuff"
    print("\n--- Exercise 3: MultiQueryRetriever ---")
    print("Base retriever results:")
    for doc in base_retriever.invoke(vague_query):
        print("  -", doc.page_content)
    print("MultiQueryRetriever results:")
    for doc in multi_query_retriever.invoke(vague_query):
        print("  -", doc.page_content)


def exercise_4():
    """Print the context documents alongside the answer to verify grounding."""
    store = _build_store()
    retriever = store.as_retriever(search_kwargs={"k": 2})
    llm = get_chat_model()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Answer using only the provided context.\n\nContext:\n{context}"),
            ("human", "{input}"),
        ]
    )
    chain = create_retrieval_chain(retriever, create_stuff_documents_chain(llm, prompt))

    print("\n--- Exercise 4: answer + grounding context ---")
    result = chain.invoke({"input": "What does create_retrieval_chain do?"})
    print("Answer:", result["answer"])
    print("Context used to generate it:")
    for doc in result["context"]:
        print("  -", doc.page_content)


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()

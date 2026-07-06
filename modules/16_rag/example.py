"""
Module 16 - RAG: load -> split -> embed -> store -> retrieve -> generate.

Run: python modules/16_rag/example.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter

from common.embedding_factory import get_embeddings
from common.model_factory import get_chat_model

HANDBOOK_PATH = Path(__file__).resolve().parent / "sample_data" / "handbook.txt"


def load_and_split() -> list[Document]:
    text = HANDBOOK_PATH.read_text(encoding="utf-8")
    splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
    chunks = splitter.split_text(text)
    return [Document(page_content=chunk, metadata={"chunk_id": i}) for i, chunk in enumerate(chunks)]


def format_docs(docs: list[Document]) -> str:
    return "\n\n".join(f"[chunk {doc.metadata['chunk_id']}] {doc.page_content}" for doc in docs)


def build_rag_chain():
    chunks = load_and_split()
    store = FAISS.from_documents(chunks, embedding=get_embeddings())
    retriever = store.as_retriever(search_kwargs={"k": 2})

    llm = get_chat_model()
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Answer the question using ONLY the context below. Cite the chunk "
                "number(s) you used, like [chunk 2]. If the answer isn't in the "
                "context, say you don't know.\n\nContext:\n{context}",
            ),
            ("human", "{question}"),
        ]
    )

    return (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )


if __name__ == "__main__":
    rag_chain = build_rag_chain()

    for question in [
        "How many days of PTO do full-time employees get, and how much can carry over?",
        "What is the company's stock buyback policy?",
    ]:
        print(f"\nQ: {question}")
        print("A:", rag_chain.invoke(question))

"""
Module 16 - Exercise solutions.

Run: python modules/16_rag/solutions.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter

from common.embedding_factory import get_embeddings
from common.model_factory import get_chat_model

HANDBOOK_PATH = Path(__file__).resolve().parent / "sample_data" / "handbook.txt"


def _format_docs(docs: list[Document]) -> str:
    return "\n\n".join(f"[chunk {doc.metadata.get('chunk_id', '?')}] {doc.page_content}" for doc in docs)


def _build_chain(chunk_size: int, k: int = 2, not_found_mode: bool = False):
    text = HANDBOOK_PATH.read_text(encoding="utf-8")
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=50)
    chunks = [Document(page_content=c, metadata={"chunk_id": i}) for i, c in enumerate(splitter.split_text(text))]
    store = FAISS.from_documents(chunks, embedding=get_embeddings())
    retriever = store.as_retriever(search_kwargs={"k": k})

    llm = get_chat_model()
    if not_found_mode:
        system = (
            "Answer using ONLY the context below. If the answer isn't in the "
            "context, respond with exactly the string NOT_FOUND and nothing else.\n\nContext:\n{context}"
        )
    else:
        system = "Answer using ONLY the context below, citing chunk numbers like [chunk 2].\n\nContext:\n{context}"

    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", "{question}")])
    return (
        {"context": retriever | _format_docs, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()
    )


def exercise_1():
    """chunk_size=150 vs chunk_size=400: observe answer/citation granularity."""
    question = "How much of unused PTO carries over to the next year?"

    print("--- Exercise 1: chunk_size comparison ---")
    for size in (400, 150):
        chain = _build_chain(chunk_size=size)
        print(f"\nchunk_size={size}:")
        print(chain.invoke(question))


def exercise_2():
    """A question requiring 2+ chunks: compare k=2 vs k=4."""
    question = (
        "Compare the parental leave policy and the equipment stipend -- "
        "how many weeks of leave, and how much is the stipend?"
    )
    print("\n--- Exercise 2: k=2 vs k=4 on a multi-fact question ---")
    for k in (2, 4):
        chain = _build_chain(chunk_size=400, k=k)
        print(f"\nk={k}:")
        print(chain.invoke(question))


def exercise_3():
    """Prompt that must respond NOT_FOUND (not prose) when context lacks the answer."""
    chain = _build_chain(chunk_size=400, not_found_mode=True)

    print("\n--- Exercise 3: NOT_FOUND mode ---")
    for question in ["What is the company's stock buyback policy?", "How many PTO days do employees get?"]:
        answer = chain.invoke(question)
        print(f"Q: {question}\nA: {answer}\nIs NOT_FOUND: {answer.strip() == 'NOT_FOUND'}\n")


def exercise_4():
    """Compare RecursiveCharacterTextSplitter vs. naive CharacterTextSplitter boundaries."""
    text = HANDBOOK_PATH.read_text(encoding="utf-8")

    recursive_chunks = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=0).split_text(text)
    naive_chunks = CharacterTextSplitter(separator="\n", chunk_size=200, chunk_overlap=0).split_text(text)

    print("\n--- Exercise 4: splitter comparison ---")
    print(f"RecursiveCharacterTextSplitter: {len(recursive_chunks)} chunks")
    print("First chunk:", repr(recursive_chunks[0][:100]))
    print(f"\nCharacterTextSplitter: {len(naive_chunks)} chunks")
    print("First chunk:", repr(naive_chunks[0][:100]))


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()

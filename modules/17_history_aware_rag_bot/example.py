"""
Module 17 - History-Aware RAG Bot: conversational RAG that resolves follow-up questions.

Run: python modules/17_history_aware_rag_bot/example.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.vectorstores import FAISS
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_text_splitters import RecursiveCharacterTextSplitter

from common.embedding_factory import get_embeddings
from common.model_factory import get_chat_model

HANDBOOK_PATH = Path(__file__).resolve().parent / "sample_data" / "handbook.txt"

_store: dict[str, BaseChatMessageHistory] = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in _store:
        _store[session_id] = ChatMessageHistory()
    return _store[session_id]


def build_retriever():
    text = HANDBOOK_PATH.read_text(encoding="utf-8")
    splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
    chunks = [Document(page_content=c) for c in splitter.split_text(text)]
    store = FAISS.from_documents(chunks, embedding=get_embeddings())
    return store.as_retriever(search_kwargs={"k": 2})


def build_conversational_rag_chain():
    llm = get_chat_model()
    retriever = build_retriever()

    # Step 1: rewrite a follow-up question into a standalone one, using history.
    contextualize_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Given the chat history and a follow-up question, rewrite it as a "
                "standalone question that makes sense without the history. Do not "
                "answer it, just rewrite it.",
            ),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_prompt)

    # Step 2: answer using the retrieved context + original history.
    answer_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Answer using only this context:\n\n{context}"),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    combine_docs_chain = create_stuff_documents_chain(llm, answer_prompt)

    rag_chain = create_retrieval_chain(history_aware_retriever, combine_docs_chain)

    return RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )


if __name__ == "__main__":
    conversational_rag = build_conversational_rag_chain()
    config = {"configurable": {"session_id": "handbook-chat"}}

    for question in [
        "How many days of PTO do full-time employees get?",
        "How much of that carries over to next year?",
        "And how many remote work days per week are allowed?",
    ]:
        result = conversational_rag.invoke({"input": question}, config=config)
        print(f"\nQ: {question}")
        print("A:", result["answer"])

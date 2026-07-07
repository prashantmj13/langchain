"""
Module 17 - Exercise solutions.

Run: python modules/17_history_aware_rag_bot/solutions.py
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
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

from common.embedding_factory import get_embeddings
from common.model_factory import get_chat_model

HANDBOOK_PATH = Path(__file__).resolve().parent / "sample_data" / "handbook.txt"

_store: dict[str, BaseChatMessageHistory] = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in _store:
        _store[session_id] = ChatMessageHistory()
    return _store[session_id]


def _build_retriever():
    text = HANDBOOK_PATH.read_text(encoding="utf-8")
    splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
    chunks = [Document(page_content=c) for c in splitter.split_text(text)]
    store = FAISS.from_documents(chunks, embedding=get_embeddings())
    return store.as_retriever(search_kwargs={"k": 2})


def _build_history_aware_retriever(llm, retriever):
    contextualize_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Rewrite the follow-up as a standalone question. Do not answer it."),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    return create_history_aware_retriever(llm, retriever, contextualize_prompt), contextualize_prompt


def exercise_1():
    """Print the rewritten standalone question for each follow-up turn."""
    llm = get_chat_model()
    retriever = _build_retriever()
    history_aware_retriever, contextualize_prompt = _build_history_aware_retriever(llm, retriever)
    rewrite_chain = contextualize_prompt | llm

    session = ChatMessageHistory()
    print("--- Exercise 1: rewritten standalone questions ---")
    for question in ["How many days of PTO do full-time employees get?", "How much of that carries over?"]:
        rewritten = rewrite_chain.invoke({"chat_history": session.messages, "input": question})
        print(f"Original:  {question}\nRewritten: {rewritten.content}\n")
        session.add_user_message(question)
        session.add_ai_message("(answer omitted for this exercise)")


def _build_full_chain():
    llm = get_chat_model()
    retriever = _build_retriever()
    history_aware_retriever, _ = _build_history_aware_retriever(llm, retriever)

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
        rag_chain, get_session_history, input_messages_key="input",
        history_messages_key="chat_history", output_messages_key="answer",
    )


def exercise_2():
    """A follow-up requiring combining two earlier turns' context."""
    chain = _build_full_chain()
    config = {"configurable": {"session_id": "ex2"}}

    print("\n--- Exercise 2: combining two earlier turns ---")
    for question in [
        "How many remote work days per week are allowed?",
        "How many days of PTO do employees get?",
        "Compare those two numbers -- which policy is more generous, remote days or PTO days?",
    ]:
        result = chain.invoke({"input": question}, config=config)
        print(f"Q: {question}\nA: {result['answer']}\n")


def exercise_3():
    """Cheaper/faster model for rewriting, Claude for the final answer."""
    try:
        rewrite_llm = get_chat_model(provider="openai", model="gpt-4o-mini")
    except Exception:  # noqa: BLE001
        rewrite_llm = get_chat_model()
    answer_llm = get_chat_model(provider="anthropic")

    retriever = _build_retriever()
    history_aware_retriever, _ = _build_history_aware_retriever(rewrite_llm, retriever)

    answer_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Answer using only this context:\n\n{context}"),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    combine_docs_chain = create_stuff_documents_chain(answer_llm, answer_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, combine_docs_chain)

    print("\n--- Exercise 3: mixed rewrite/answer models ---")
    result = rag_chain.invoke({"input": "How many PTO days do employees get?", "chat_history": []})
    print(result["answer"])


def exercise_4():
    """Rebuild as a LangGraph agent with the retriever exposed as a tool."""
    retriever = _build_retriever()

    @tool
    def search_handbook(query: str) -> str:
        """Search the employee handbook for relevant policy text."""
        docs = retriever.invoke(query)
        return "\n\n".join(doc.page_content for doc in docs)

    llm = get_chat_model()
    agent = create_react_agent(llm, tools=[search_handbook])

    print("\n--- Exercise 4: retriever-as-tool agent ---")
    result = agent.invoke(
        {"messages": [("human", "How many days of PTO do full-time employees get, and how much carries over?")]}
    )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()

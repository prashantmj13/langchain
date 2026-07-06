"""
Module 07 - Chat History with RunnableWithMessageHistory.

Run: python modules/07_chat_history/example.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

from common.model_factory import get_chat_model

# session_id -> BaseChatMessageHistory
_store: dict[str, BaseChatMessageHistory] = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in _store:
        _store[session_id] = ChatMessageHistory()
    return _store[session_id]


def build_chain_with_history():
    llm = get_chat_model()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a concise, friendly assistant."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )
    chain = prompt | llm

    return RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )


if __name__ == "__main__":
    chain_with_history = build_chain_with_history()

    print("--- Session: alice ---")
    for message in [
        "Hi, my name is Alice and I'm learning LangChain.",
        "What's a good first project to build?",
        "What did I just ask you about?",
    ]:
        response = chain_with_history.invoke(
            {"input": message}, config={"configurable": {"session_id": "alice"}}
        )
        print(f"> {message}")
        print(response.content, "\n")

    print("--- Session: bob (independent history) ---")
    response = chain_with_history.invoke(
        {"input": "Do you know my name?"}, config={"configurable": {"session_id": "bob"}}
    )
    print("> Do you know my name?")
    print(response.content)
    print("\n(Bob's session has no knowledge of Alice's conversation.)")

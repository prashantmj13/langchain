"""
Module 07 - Exercise solutions.

Run: python modules/07_chat_history/solutions.py
"""

import json
import sys
import threading
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage, messages_from_dict, messages_to_dict
from langchain_core.messages.utils import trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

from common.model_factory import get_chat_model

_store: dict[str, BaseChatMessageHistory] = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in _store:
        _store[session_id] = ChatMessageHistory()
    return _store[session_id]


def _build_chain():
    llm = get_chat_model()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a concise, friendly assistant."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )
    return RunnableWithMessageHistory(
        prompt | llm, get_session_history, input_messages_key="input", history_messages_key="history"
    )


def exercise_1():
    """Add a 4th turn asking Alice to summarize the conversation so far."""
    chain = _build_chain()
    config = {"configurable": {"session_id": "alice-ex1"}}

    print("--- Exercise 1: summarize the conversation ---")
    for message in [
        "Hi, my name is Alice and I'm learning LangChain.",
        "What's a good first project to build?",
        "What did I just ask you about?",
        "Summarize our conversation so far in 2 sentences.",
    ]:
        response = chain.invoke({"input": message}, config=config)
        print(f"> {message}\n{response.content}\n")


def exercise_2():
    """Trim history to the last 6 messages before it's passed into the prompt."""
    llm = get_chat_model()
    history = get_session_history("trim-demo")
    history.clear()

    for i in range(10):
        history.add_user_message(f"Message number {i}")
        history.add_ai_message(f"Acknowledged message {i}")

    trimmed = trim_messages(
        history.messages, max_tokens=6, strategy="last", token_counter=len, allow_partial=False
    )

    print("\n--- Exercise 2: trimmed history ---")
    print(f"Full history: {len(history.messages)} messages")
    print(f"Trimmed history: {len(trimmed)} messages")
    for m in trimmed:
        print(" -", m.content)


class JsonFileChatMessageHistory(BaseChatMessageHistory):
    """A minimal JSON-file-backed chat message history."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        if not self.file_path.exists():
            self.file_path.write_text("[]", encoding="utf-8")

    @property
    def messages(self):
        raw = json.loads(self.file_path.read_text(encoding="utf-8"))
        return messages_from_dict(raw)

    def add_message(self, message) -> None:
        current = messages_to_dict(self.messages)
        current.append(messages_to_dict([message])[0])
        self.file_path.write_text(json.dumps(current), encoding="utf-8")

    def clear(self) -> None:
        self.file_path.write_text("[]", encoding="utf-8")


def exercise_3():
    """Swap the in-memory store for a JSON-file-backed store that persists to disk."""
    file_path = Path(__file__).resolve().parent / "chat_history_demo.json"
    history = JsonFileChatMessageHistory(file_path)
    history.clear()

    history.add_message(HumanMessage(content="Hello, this should persist to disk."))
    history.add_message(AIMessage(content="Got it, saved to a JSON file."))

    print("\n--- Exercise 3: JSON-file-backed history ---")
    print(f"Wrote {len(history.messages)} messages to {file_path}")

    # Simulate a fresh process reading it back.
    reloaded = JsonFileChatMessageHistory(file_path)
    print(f"Reloaded {len(reloaded.messages)} messages from disk:", [m.content for m in reloaded.messages])


def exercise_4():
    """Run two sessions concurrently, confirm no cross-contamination."""
    chain = _build_chain()

    def run_session(session_id: str, name: str):
        chain.invoke(
            {"input": f"Hi, my name is {name}."}, config={"configurable": {"session_id": session_id}}
        )

    threads = [
        threading.Thread(target=run_session, args=("carol", "Carol")),
        threading.Thread(target=run_session, args=("dave", "Dave")),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    carol_history = get_session_history("carol").messages
    dave_history = get_session_history("dave").messages

    print("\n--- Exercise 4: concurrent sessions ---")
    print("Carol's history has 'Dave':", any("Dave" in m.content for m in carol_history))
    print("Dave's history has 'Carol':", any("Carol" in m.content for m in dave_history))
    print("(Both should be False -- sessions never cross-contaminate.)")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()

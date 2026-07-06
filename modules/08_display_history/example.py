"""
Module 08 - Display History: formatting a conversation transcript.

Run: python modules/08_display_history/example.py
"""

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import BaseMessage

from common.model_factory import get_chat_model


def run_short_conversation() -> ChatMessageHistory:
    llm = get_chat_model()
    history = ChatMessageHistory()

    for user_input in ["What is a vector database?", "Give me one popular example."]:
        history.add_user_message(user_input)
        response = llm.invoke(history.messages)
        history.add_ai_message(response.content)

    return history


def print_transcript(history: ChatMessageHistory) -> None:
    print("--- Console transcript ---")
    for message in history.messages:
        role = message.type.upper()
        print(f"[{role}] {message.content}")


def to_markdown(history: ChatMessageHistory) -> str:
    lines = []
    for message in history.messages:
        speaker = "**You**" if message.type == "human" else "**Assistant**"
        lines.append(f"{speaker}: {message.content}")
    return "\n\n".join(lines)


def to_json(history: ChatMessageHistory) -> str:
    serializable = [
        {"role": message.type, "content": message.content} for message in history.messages
    ]
    return json.dumps(serializable, indent=2)


def messages_from_json(payload: str) -> list[BaseMessage]:
    from langchain_core.messages import AIMessage, HumanMessage

    role_to_cls = {"human": HumanMessage, "ai": AIMessage}
    return [role_to_cls[item["role"]](content=item["content"]) for item in json.loads(payload)]


if __name__ == "__main__":
    convo = run_short_conversation()

    print_transcript(convo)

    print("\n--- Markdown transcript ---")
    print(to_markdown(convo))

    print("\n--- JSON transcript ---")
    json_payload = to_json(convo)
    print(json_payload)

    reloaded = messages_from_json(json_payload)
    print(f"\nReloaded {len(reloaded)} messages from JSON.")

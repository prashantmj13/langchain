"""
Module 01 - LangChain Basics.

Run: python modules/01_langchain_basics/example.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import HumanMessage, SystemMessage

from common.model_factory import get_chat_model


def basic_invoke():
    llm = get_chat_model()
    response = llm.invoke([HumanMessage(content="What is LangChain in one sentence?")])
    print("--- Basic invoke ---")
    print(response.content)
    print("Token usage:", response.usage_metadata)


def system_plus_human():
    llm = get_chat_model()
    messages = [
        SystemMessage(content="You are a terse senior Python engineer. Answer in <= 2 sentences."),
        HumanMessage(content="Why would I use a virtual environment?"),
    ]
    response = llm.invoke(messages)
    print("\n--- System + Human ---")
    print(response.content)


def streaming():
    llm = get_chat_model()
    print("\n--- Streaming ---")
    for chunk in llm.stream([HumanMessage(content="Count from 1 to 5, one number per line.")]):
        print(chunk.content, end="", flush=True)
    print()


if __name__ == "__main__":
    basic_invoke()
    system_plus_human()
    streaming()

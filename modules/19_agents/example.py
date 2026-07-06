"""
Module 19 - Agents: a LangGraph ReAct agent with local tools.

Run: python modules/19_agents/example.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from common.model_factory import get_chat_model


@tool
def add(a: float, b: float) -> float:
    """Add two numbers together and return the sum."""
    return a + b


@tool
def get_word_length(word: str) -> int:
    """Return the number of characters in a word."""
    return len(word)


def build_agent():
    llm = get_chat_model()
    return create_react_agent(llm, tools=[add, get_word_length])


if __name__ == "__main__":
    agent = build_agent()
    question = "How much longer is the word 'LangChain' than the sum of 3 and 4?"

    result = agent.invoke({"messages": [("human", question)]})

    print("--- Full message trace ---")
    for message in result["messages"]:
        message.pretty_print()

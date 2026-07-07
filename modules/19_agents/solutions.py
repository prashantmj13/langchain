"""
Module 19 - Exercise solutions.

Run: python modules/19_agents/solutions.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import ToolMessage
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


@tool
def reverse_string(s: str) -> str:
    """Reverse the given string."""
    return s[::-1]


def exercise_1():
    """Add reverse_string, ask a question requiring all three tools."""
    llm = get_chat_model()
    agent = create_react_agent(llm, tools=[add, get_word_length, reverse_string])

    question = (
        "Reverse the word 'LangChain', then tell me how many characters the "
        "reversed word has, then add that number to 10."
    )
    result = agent.invoke({"messages": [("human", question)]})
    print("--- Exercise 1: 3-tool question ---")
    print(result["messages"][-1].content)


def exercise_2():
    """Print each intermediate ToolMessage's exact arguments/results."""
    llm = get_chat_model()
    agent = create_react_agent(llm, tools=[add, get_word_length])

    question = "How much longer is the word 'observability' than the sum of 2 and 5?"
    result = agent.invoke({"messages": [("human", question)]})

    print("\n--- Exercise 2: tool call trace ---")
    for message in result["messages"]:
        if hasattr(message, "tool_calls") and message.tool_calls:
            for call in message.tool_calls:
                print(f"Called {call['name']} with args {call['args']}")
        if isinstance(message, ToolMessage):
            print(f"  -> result: {message.content}")


@tool
def flaky_divide(a: float, b: float) -> float:
    """Divide a by b. Raises an error if b is zero."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b


def exercise_3():
    """A tool that raises for certain inputs -- observe how the agent recovers."""
    llm = get_chat_model()
    agent = create_react_agent(llm, tools=[flaky_divide])

    print("\n--- Exercise 3: tool error recovery ---")
    result = agent.invoke({"messages": [("human", "What is 10 divided by 0?")]})
    for message in result["messages"]:
        message.pretty_print()


@tool
def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b


@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


@tool
def divide(a: float, b: float) -> float:
    """Divide a by b."""
    return a / b


def exercise_4():
    """4 separate arithmetic tools, a multi-step question requiring several calls."""
    llm = get_chat_model()
    agent = create_react_agent(llm, tools=[add, subtract, multiply, divide])

    question = "Take 20, add 15, subtract 5, multiply by 2, then divide by 4. What's the final result?"
    result = agent.invoke({"messages": [("human", question)]})

    print("\n--- Exercise 4: multi-step arithmetic ---")
    print(result["messages"][-1].content)


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()

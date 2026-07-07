"""
Module 01 - Exercise solutions.

Run: python modules/01_langchain_basics/solutions.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import HumanMessage, SystemMessage

from common.model_factory import get_chat_model

# Illustrative only -- check https://www.anthropic.com/pricing for current rates.
PRICE_PER_MILLION_INPUT_TOKENS_USD = 3.0
PRICE_PER_MILLION_OUTPUT_TOKENS_USD = 15.0


def exercise_1():
    """Pirate-persona system prompt, held across three different questions."""
    llm = get_chat_model()
    system = SystemMessage(content="You always answer in the voice of a friendly pirate.")

    print("--- Exercise 1: pirate persona ---")
    for question in [
        "What is a variable in Python?",
        "How do I open a file?",
        "What's your favorite programming language?",
    ]:
        response = llm.invoke([system, HumanMessage(content=question)])
        print(f"> {question}\n{response.content}\n")


def exercise_2():
    """Print usage metadata and compute an approximate cost for the call."""
    llm = get_chat_model()
    response = llm.invoke([HumanMessage(content="Explain recursion in one sentence.")])

    usage = response.usage_metadata
    input_cost = (usage["input_tokens"] / 1_000_000) * PRICE_PER_MILLION_INPUT_TOKENS_USD
    output_cost = (usage["output_tokens"] / 1_000_000) * PRICE_PER_MILLION_OUTPUT_TOKENS_USD

    print("--- Exercise 2: usage metadata + approximate cost ---")
    print("usage_metadata:", usage)
    print(f"approx cost: ${input_cost + output_cost:.6f}")


def exercise_3():
    """Stream the system+human example chunk by chunk instead of invoking."""
    llm = get_chat_model()
    messages = [
        SystemMessage(content="You are a terse senior Python engineer. Answer in <= 2 sentences."),
        HumanMessage(content="Why would I use a virtual environment?"),
    ]

    print("--- Exercise 3: streaming ---")
    for chunk in llm.stream(messages):
        print(chunk.content, end="", flush=True)
    print()


def exercise_4():
    """
    Swap LLM_PROVIDER to 'ollama' with a local model pulled (`ollama pull llama3.1`)
    and confirm the same script runs unmodified.

    There's no code change here -- that's the point of common/model_factory.py.
    Set this in your .env:
        LLM_PROVIDER=ollama
    Then re-run exercise_1()/exercise_3() unchanged; get_chat_model() will
    instantiate ChatOllama instead of ChatAnthropic automatically.
    """
    import os

    print("--- Exercise 4 ---")
    print(f"Current LLM_PROVIDER: {os.getenv('LLM_PROVIDER', 'anthropic (default)')}")
    print("Change LLM_PROVIDER in .env to 'ollama' and re-run this file -- no code changes needed.")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()

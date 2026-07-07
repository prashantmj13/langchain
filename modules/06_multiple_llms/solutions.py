"""
Module 06 - Exercise solutions.

Run: python modules/06_multiple_llms/solutions.py
"""

import sys
import time
from collections import Counter
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableBranch

from common.model_factory import get_chat_model


def exercise_1():
    """Add Google Gemini to the comparison, print answers + latency for all 4."""
    print("--- Exercise 1: 4-provider comparison ---")
    for provider in ("anthropic", "openai", "google", "ollama"):
        try:
            llm = get_chat_model(provider=provider)
            start = time.perf_counter()
            response = llm.invoke("What is the capital of Australia?")
            elapsed = time.perf_counter() - start
            print(f"[{provider}] ({elapsed:.2f}s) {response.content[:150]}")
        except Exception as exc:  # noqa: BLE001
            print(f"[{provider}] skipped ({exc.__class__.__name__}: {exc})")


def exercise_2():
    """Route anything containing 'code' to Claude, regardless of task_type tag."""
    reasoning_llm = get_chat_model(provider="anthropic")
    try:
        simple_llm = get_chat_model(provider="openai", model="gpt-4o-mini")
    except Exception:  # noqa: BLE001
        simple_llm = reasoning_llm

    prompt = ChatPromptTemplate.from_messages([("human", "{question}")])
    reasoning_chain = prompt | reasoning_llm | StrOutputParser()
    simple_chain = prompt | simple_llm | StrOutputParser()

    router = RunnableBranch(
        (lambda x: "code" in x["question"].lower(), reasoning_chain),
        (lambda x: x["task_type"] == "reasoning", reasoning_chain),
        simple_chain,
    )

    print("\n--- Exercise 2: 'code' always routes to Claude ---")
    for task_type, question in [
        ("simple lookup", "Write code to reverse a linked list in Python."),
        ("simple lookup", "What is the capital of Japan?"),
    ]:
        result = router.invoke({"task_type": task_type, "question": question})
        print(f"[{task_type}] {question[:50]!r} -> {result[:120]}")


def exercise_3():
    """Voting ensemble: 3 models answer the same yes/no question, print majority."""
    question = "Is Python a compiled language? Answer with exactly one word: yes or no."
    votes = []
    for provider in ("anthropic", "openai", "ollama"):
        try:
            llm = get_chat_model(provider=provider)
            answer = llm.invoke(question).content.strip().lower()
            votes.append(answer)
        except Exception:  # noqa: BLE001
            continue

    print("\n--- Exercise 3: voting ensemble ---")
    print("Votes:", votes)
    if votes:
        majority, count = Counter(votes).most_common(1)[0]
        print(f"Majority answer: {majority} ({count}/{len(votes)} votes)")


def exercise_4():
    """Compare draft-and-polish cost vs. asking Claude directly, via usage metadata."""
    topic = "why caching matters in web APIs"

    try:
        draft_llm = get_chat_model(provider="openai", model="gpt-4o-mini", temperature=0.9)
    except Exception:  # noqa: BLE001
        draft_llm = get_chat_model(temperature=0.9)
    polish_llm = get_chat_model(provider="anthropic", temperature=0.2)

    draft_prompt = ChatPromptTemplate.from_messages(
        [("human", "Write a rough one-paragraph draft explaining: {topic}")]
    )
    polish_prompt = ChatPromptTemplate.from_messages(
        [("human", "Polish and tighten this draft, keep it to 2 sentences:\n\n{draft}")]
    )

    draft_response = (draft_prompt | draft_llm).invoke({"topic": topic})
    polish_response = (polish_prompt | polish_llm).invoke({"draft": draft_response.content})

    direct_prompt = ChatPromptTemplate.from_messages(
        [("human", "In 2 sentences, explain: {topic}")]
    )
    direct_response = (direct_prompt | get_chat_model(provider="anthropic")).invoke({"topic": topic})

    print("\n--- Exercise 4: draft-and-polish vs. direct, token usage ---")
    print("Draft usage:  ", getattr(draft_response, "usage_metadata", "n/a"))
    print("Polish usage: ", polish_response.usage_metadata)
    print("Direct usage: ", direct_response.usage_metadata)


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()

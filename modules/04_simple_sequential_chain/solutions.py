"""
Module 04 - Exercise solutions.

Run: python modules/04_simple_sequential_chain/solutions.py
"""

import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from common.model_factory import get_chat_model


def build_stage_1(temperature: float = 0.7):
    llm = get_chat_model(temperature=temperature)
    prompt = ChatPromptTemplate.from_messages(
        [("human", "Write a 3-bullet outline for a short blog post about: {topic}")]
    )
    return prompt | llm | StrOutputParser()


def build_stage_2(temperature: float = 0.7):
    llm = get_chat_model(temperature=temperature)
    prompt = ChatPromptTemplate.from_messages(
        [("human", "Given this outline, write a punchy 2-sentence opening paragraph:\n\n{outline}")]
    )
    return prompt | llm | StrOutputParser()


def build_stage_3():
    llm = get_chat_model()
    prompt = ChatPromptTemplate.from_messages(
        [("human", "Given this opening paragraph, write one punchy title (<=8 words):\n\n{paragraph}")]
    )
    return prompt | llm | StrOutputParser()


def exercise_1():
    """Add a 3rd stage producing a punchy title from the opening paragraph."""
    stage_1, stage_2, stage_3 = build_stage_1(), build_stage_2(), build_stage_3()

    outline = stage_1.invoke({"topic": "why vector databases matter"})
    opening = stage_2.invoke({"outline": outline})
    title = stage_3.invoke({"paragraph": opening})

    print("--- Exercise 1: 3-stage chain ---")
    print("Title:  ", title)
    print("Opening:", opening)


def exercise_2():
    """Print intermediate outline separately from the final paragraph."""
    stage_1, stage_2 = build_stage_1(), build_stage_2()

    outline = stage_1.invoke({"topic": "the benefits of code review"})
    print("\n--- Exercise 2: intermediate output ---")
    print("Outline (intermediate):\n", outline)

    opening = stage_2.invoke({"outline": outline})
    print("\nOpening paragraph (final):\n", opening)


def exercise_3():
    """Stage 1 at temperature=0.9 (creative), stage 2 at temperature=0.2 (focused)."""
    stage_1 = build_stage_1(temperature=0.9)
    stage_2 = build_stage_2(temperature=0.2)

    outline = stage_1.invoke({"topic": "the future of remote work"})
    opening = stage_2.invoke({"outline": outline})

    print("\n--- Exercise 3: mixed temperatures ---")
    print("Outline:", outline)
    print("Opening:", opening)


def exercise_4():
    """Time the composed chain vs manual step-by-step invocation."""
    stage_1, stage_2 = build_stage_1(), build_stage_2()
    full_chain = stage_1 | (lambda outline_text: {"outline": outline_text}) | stage_2

    start = time.perf_counter()
    full_chain.invoke({"topic": "why caching matters"})
    composed_time = time.perf_counter() - start

    start = time.perf_counter()
    outline = stage_1.invoke({"topic": "why caching matters"})
    stage_2.invoke({"outline": outline})
    manual_time = time.perf_counter() - start

    print("\n--- Exercise 4: timing ---")
    print(f"Composed chain: {composed_time:.2f}s")
    print(f"Manual steps:   {manual_time:.2f}s (about the same -- LCEL adds no overhead)")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()

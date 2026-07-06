"""
Module 04 - Simple Sequential Chain (single input/output at every stage).

Run: python modules/04_simple_sequential_chain/example.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from common.model_factory import get_chat_model


def build_stage_1():
    llm = get_chat_model()
    prompt = ChatPromptTemplate.from_messages(
        [("human", "Write a 3-bullet outline for a short blog post about: {topic}")]
    )
    return prompt | llm | StrOutputParser()


def build_stage_2():
    llm = get_chat_model()
    prompt = ChatPromptTemplate.from_messages(
        [("human", "Given this outline, write a punchy 2-sentence opening paragraph:\n\n{outline}")]
    )
    return prompt | llm | StrOutputParser()


if __name__ == "__main__":
    stage_1 = build_stage_1()
    stage_2 = build_stage_2()

    # Step-by-step, so intermediate output is visible.
    outline = stage_1.invoke({"topic": "why vector databases matter"})
    print("--- Stage 1 output (outline) ---")
    print(outline)

    opening = stage_2.invoke({"outline": outline})
    print("\n--- Stage 2 output (opening paragraph) ---")
    print(opening)

    # Same result, composed into a single simple sequential chain.
    full_chain = stage_1 | (lambda outline_text: {"outline": outline_text}) | stage_2
    print("\n--- Composed chain (single call) ---")
    print(full_chain.invoke({"topic": "why vector databases matter"}))

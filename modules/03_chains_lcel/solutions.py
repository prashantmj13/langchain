"""
Module 03 - Exercise solutions.

Run: python modules/03_chains_lcel/solutions.py
"""

import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel, Field

from common.model_factory import get_chat_model


def exercise_1():
    """Add a 4th stage that counts words and formats '{n} words: {text}'."""
    llm = get_chat_model()
    prompt = ChatPromptTemplate.from_messages([("human", "Explain {topic} in one short sentence.")])
    count_words = RunnableLambda(lambda text: f"{len(text.split())} words: {text}")

    chain = prompt | llm | StrOutputParser() | count_words
    print("--- Exercise 1: word count stage ---")
    print(chain.invoke({"topic": "recursion"}))


class MovieReview(BaseModel):
    title: str = Field(description="Movie title")
    rating: int = Field(description="Rating out of 10")
    summary: str = Field(description="One-sentence summary of the review")


def exercise_2():
    """Extract structured MovieReview data from a different free-text review."""
    llm = get_chat_model()
    structured_llm = llm.with_structured_output(MovieReview)
    prompt = ChatPromptTemplate.from_messages([("human", "Extract structured data:\n\n{review}")])
    chain = prompt | structured_llm

    review = (
        "Oppenheimer was a gripping, tense biopic with career-best performances. "
        "I'd rate it an 8 out of 10 -- a bit long, but well worth it."
    )
    print("\n--- Exercise 2: structured output ---")
    print(chain.invoke({"review": review}))


def exercise_3():
    """Compare .batch() vs a plain for loop of .invoke() calls."""
    llm = get_chat_model()
    prompt = ChatPromptTemplate.from_messages([("human", "Name one famous {thing}.")])
    chain = prompt | llm | StrOutputParser()
    inputs = [{"thing": t} for t in ["mathematician", "painter", "physicist", "chef", "architect"]]

    start = time.perf_counter()
    batch_results = chain.batch(inputs)
    batch_time = time.perf_counter() - start

    start = time.perf_counter()
    loop_results = [chain.invoke(item) for item in inputs]
    loop_time = time.perf_counter() - start

    print("\n--- Exercise 3: batch vs loop timing ---")
    print(f"batch(): {batch_time:.2f}s")
    print(f"for loop: {loop_time:.2f}s")
    assert len(batch_results) == len(loop_results) == 5


def exercise_4():
    """Stream the full 3-stage chain, printing output as it arrives."""
    llm = get_chat_model()
    prompt = ChatPromptTemplate.from_messages([("human", "List 3 benefits of unit testing.")])
    chain = prompt | llm | StrOutputParser()

    print("\n--- Exercise 4: streaming the full chain ---")
    for chunk in chain.stream({}):
        print(chunk, end="", flush=True)
    print()


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()

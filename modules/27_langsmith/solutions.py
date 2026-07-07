"""
Module 27 - Exercise solutions.

Run: python modules/27_langsmith/solutions.py
"""

import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable

from common.model_factory import get_chat_model

load_dotenv()


def exercise_1():
    """
    Set LANGSMITH_TRACING=true and LANGSMITH_API_KEY in .env, then re-run this
    file and look for the trace at https://smith.langchain.com/ under the
    project named by LANGSMITH_PROJECT. There's no code change needed --
    that's the point of env-var-based tracing.
    """
    print("--- Exercise 1 ---")
    configured = os.getenv("LANGSMITH_TRACING", "").lower() == "true" and bool(os.getenv("LANGSMITH_API_KEY"))
    print(f"Tracing currently configured: {configured}")
    if not configured:
        print("Set LANGSMITH_TRACING=true and LANGSMITH_API_KEY in .env, then re-run.")


@traceable(name="fetch_topic_facts")
def fetch_topic_facts(topic: str) -> str:
    """A parent traced function."""
    return summarize_facts(f"Facts about {topic}: it is widely used, well documented, open source.")


@traceable(name="summarize_facts")
def summarize_facts(facts: str) -> str:
    """A nested traced function -- should appear as a child of fetch_topic_facts in the UI."""
    return facts[:50] + ("..." if len(facts) > 50 else "")


def exercise_2():
    """A second @traceable function nested inside the first."""
    print("\n--- Exercise 2: nested @traceable functions ---")
    print(fetch_topic_facts("LangSmith"))
    print("(In the LangSmith UI, summarize_facts should appear nested under fetch_topic_facts.)")


EXPANDED_DATASET = [
    {"topic": "LangSmith", "expected_substring": "trac", "max_words": 40},
    {"topic": "a vector database", "expected_substring": "vector", "max_words": 40},
    {"topic": "an MCP server", "expected_substring": "tool", "max_words": 40},
    {"topic": "RAG", "expected_substring": "retriev", "max_words": 40},
    {"topic": "an embedding", "expected_substring": "vector", "max_words": 40},
    {"topic": "LangGraph", "expected_substring": "graph", "max_words": 40},
    {"topic": "a chat model", "expected_substring": "model", "max_words": 40},
    {"topic": "a prompt template", "expected_substring": "prompt", "max_words": 40},
    {"topic": "FAISS", "expected_substring": "search", "max_words": 40},
    {"topic": "an agent", "expected_substring": "tool", "max_words": 40},
]


def _build_chain(system_message: str):
    llm = get_chat_model()
    prompt = ChatPromptTemplate.from_messages([("system", system_message), ("human", "{topic}")])
    return prompt | llm | StrOutputParser()


def exercise_3():
    """10-example dataset with two graders: substring match + response length."""
    chain = _build_chain("In one sentence, what is {topic}? Reply only with the sentence.")

    print("\n--- Exercise 3: 10-example evaluation, two graders ---")
    substring_passes = length_passes = 0
    for case in EXPANDED_DATASET:
        output = chain.invoke({"topic": case["topic"]})
        substring_ok = case["expected_substring"].lower() in output.lower()
        length_ok = len(output.split()) <= case["max_words"]
        substring_passes += substring_ok
        length_passes += length_ok
        print(f"[{'PASS' if substring_ok else 'FAIL'}/{'PASS' if length_ok else 'FAIL'}] {case['topic']}: {output}")

    print(f"\nSubstring check: {substring_passes}/{len(EXPANDED_DATASET)}")
    print(f"Length check:     {length_passes}/{len(EXPANDED_DATASET)}")


def exercise_4():
    """Compare two prompt variants against the same dataset."""
    variant_a = _build_chain("In one sentence, what is {topic}? Reply only with the sentence.")
    variant_b = _build_chain("Explain {topic} to a beginner in exactly one clear, simple sentence.")

    print("\n--- Exercise 4: comparing two prompt variants ---")
    for label, chain in [("A (terse)", variant_a), ("B (beginner-friendly)", variant_b)]:
        passes = 0
        for case in EXPANDED_DATASET[:5]:
            output = chain.invoke({"topic": case["topic"]})
            passes += case["expected_substring"].lower() in output.lower()
        print(f"Variant {label}: {passes}/5 passed substring check")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()

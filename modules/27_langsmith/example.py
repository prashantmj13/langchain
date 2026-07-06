"""
Module 27 - LangSmith: tracing via env vars, @traceable, and a minimal local evaluation.

Run: python modules/27_langsmith/example.py

Set LANGSMITH_TRACING=true and LANGSMITH_API_KEY in .env to see traces show up at
https://smith.langchain.com/ -- without them, this script still runs, just untraced.
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


def check_tracing_configured() -> bool:
    enabled = os.getenv("LANGSMITH_TRACING", "").lower() == "true" and bool(os.getenv("LANGSMITH_API_KEY"))
    if not enabled:
        print(
            "LangSmith tracing is not configured (set LANGSMITH_TRACING=true and "
            "LANGSMITH_API_KEY in .env to see traces at https://smith.langchain.com/).\n"
            "Continuing without tracing.\n"
        )
    return enabled


@traceable(name="shorten_for_display")
def shorten_for_display(text: str, max_len: int = 80) -> str:
    """A plain Python post-processing step, traced alongside the LLM call."""
    return text if len(text) <= max_len else text[: max_len - 3] + "..."


def build_chain():
    llm = get_chat_model()
    prompt = ChatPromptTemplate.from_messages([("human", "In one sentence, what is {topic}?")])
    return prompt | llm | StrOutputParser()


EVAL_DATASET = [
    {"topic": "LangSmith", "expected_substring": "trac"},
    {"topic": "a vector database", "expected_substring": "vector"},
    {"topic": "an MCP server", "expected_substring": "tool"},
]


def run_mini_evaluation(chain) -> None:
    print("--- Mini evaluation (local, substring check) ---")
    passed = 0
    for case in EVAL_DATASET:
        output = chain.invoke({"topic": case["topic"]})
        ok = case["expected_substring"].lower() in output.lower()
        passed += ok
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] topic={case['topic']!r} -> {output}")
    print(f"\n{passed}/{len(EVAL_DATASET)} passed")


if __name__ == "__main__":
    check_tracing_configured()

    rag_style_chain = build_chain()
    result = rag_style_chain.invoke({"topic": "retrieval-augmented generation"})
    print("--- Chain output (traced automatically if tracing is enabled) ---")
    print(result)
    print("\n--- Post-processed with @traceable ---")
    print(shorten_for_display(result))

    print()
    run_mini_evaluation(rag_style_chain)

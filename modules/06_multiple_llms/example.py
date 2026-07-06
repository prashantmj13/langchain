"""
Module 06 - Multiple LLMs: comparison, routing, and draft-and-polish.

Run: python modules/06_multiple_llms/example.py

Note: the OpenAI and Ollama sections require OPENAI_API_KEY / a running local
Ollama daemon respectively. They're wrapped in try/except so the script still
demonstrates Claude-only behavior if those aren't configured.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableBranch

from common.model_factory import get_chat_model

QUESTION = "What is the time complexity of binary search, and why?"


def compare_providers():
    print("--- Comparing providers on the same question ---")
    for provider in ("anthropic", "openai", "ollama"):
        try:
            llm = get_chat_model(provider=provider)
            response = llm.invoke(QUESTION)
            print(f"\n[{provider}]\n{response.content}")
        except Exception as exc:  # noqa: BLE001 - demo script, provider may not be configured
            print(f"\n[{provider}] skipped ({exc.__class__.__name__}: {exc})")


def routing_example():
    print("\n--- Routing by task type ---")
    reasoning_llm = get_chat_model(provider="anthropic")
    try:
        simple_llm = get_chat_model(provider="openai", model="gpt-4o-mini")
    except Exception:  # noqa: BLE001
        simple_llm = reasoning_llm  # fall back so the demo still runs

    prompt = ChatPromptTemplate.from_messages([("human", "{question}")])
    reasoning_chain = prompt | reasoning_llm | StrOutputParser()
    simple_chain = prompt | simple_llm | StrOutputParser()

    router = RunnableBranch(
        (lambda x: x["task_type"] == "reasoning", reasoning_chain),
        simple_chain,  # default branch
    )

    for task_type, question in [
        ("reasoning", "Prove that the square root of 2 is irrational."),
        ("simple lookup", "What is the capital of Japan?"),
    ]:
        result = router.invoke({"task_type": task_type, "question": question})
        print(f"\n[{task_type}] -> {result[:200]}")


def draft_and_polish():
    print("\n--- Draft-and-polish pipeline ---")
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

    draft_chain = draft_prompt | draft_llm | StrOutputParser()
    polish_chain = draft_chain | (lambda draft: {"draft": draft}) | polish_prompt | polish_llm | StrOutputParser()

    print(polish_chain.invoke({"topic": "why caching matters in web APIs"}))


if __name__ == "__main__":
    compare_providers()
    routing_example()
    draft_and_polish()

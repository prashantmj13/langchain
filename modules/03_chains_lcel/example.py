"""
Module 03 - Chains with LCEL.

Run: python modules/03_chains_lcel/example.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel, Field

from common.model_factory import get_chat_model


def basic_lcel_chain():
    llm = get_chat_model()
    prompt = ChatPromptTemplate.from_messages(
        [("human", "Explain {topic} in exactly two short sentences.")]
    )
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"topic": "the LCEL pipe operator"})
    print("--- Basic LCEL chain ---")
    print(result)
    return chain


def chain_with_lambda(chain):
    shout_keyword = RunnableLambda(lambda text: text.replace("LCEL", "**LCEL**"))
    full_chain = chain | shout_keyword
    result = full_chain.invoke({"topic": "the LCEL pipe operator"})
    print("\n--- Chain + RunnableLambda ---")
    print(result)


class MovieReview(BaseModel):
    title: str = Field(description="Movie title")
    rating: int = Field(description="Rating out of 10")
    summary: str = Field(description="One-sentence summary of the review")


def structured_output_chain():
    llm = get_chat_model()
    structured_llm = llm.with_structured_output(MovieReview)
    prompt = ChatPromptTemplate.from_messages(
        [("human", "Extract structured data from this review:\n\n{review}")]
    )
    chain = prompt | structured_llm
    result = chain.invoke(
        {
            "review": (
                "Dune: Part Two was visually stunning and the sound design was incredible. "
                "I'd give it a 9 out of 10 -- a near-perfect sci-fi epic."
            )
        }
    )
    print("\n--- Structured output ---")
    print(result)


def batching():
    llm = get_chat_model()
    prompt = ChatPromptTemplate.from_messages([("human", "Name one famous {thing}.")])
    chain = prompt | llm | StrOutputParser()
    results = chain.batch(
        [{"thing": "mathematician"}, {"thing": "painter"}, {"thing": "physicist"}]
    )
    print("\n--- Batch ---")
    for r in results:
        print("-", r)


if __name__ == "__main__":
    base_chain = basic_lcel_chain()
    chain_with_lambda(base_chain)
    structured_output_chain()
    batching()

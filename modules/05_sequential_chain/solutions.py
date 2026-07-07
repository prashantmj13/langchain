"""
Module 05 - Exercise solutions.

Run: python modules/05_sequential_chain/solutions.py
"""

import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from pydantic import BaseModel, Field

from common.model_factory import get_chat_model

REVIEW = (
    "The headphones arrived two days late and the box was dented, but honestly the "
    "sound quality is fantastic and the noise cancelling is better than my old pair."
)


def _sentiment_chain(llm):
    return (
        ChatPromptTemplate.from_messages(
            [("human", "In one word (positive/negative/mixed), what is the sentiment of:\n\n{review}")]
        )
        | llm
        | StrOutputParser()
    )


def _summary_chain(llm):
    return (
        ChatPromptTemplate.from_messages([("human", "Summarize this review in one sentence:\n\n{review}")])
        | llm
        | StrOutputParser()
    )


def exercise_1():
    """Add a 4th parallel branch extracting complaint categories."""
    llm = get_chat_model()
    categories_chain = (
        ChatPromptTemplate.from_messages(
            [
                (
                    "human",
                    "List complaint categories mentioned in this review as a comma-separated "
                    "list (choose from: shipping, quality, price, packaging, other). "
                    "If none, say 'none'.\n\n{review}",
                )
            ]
        )
        | llm
        | StrOutputParser()
    )

    enrich = RunnablePassthrough.assign(
        sentiment=_sentiment_chain(llm),
        summary=_summary_chain(llm),
        categories=categories_chain,
    )
    result = enrich.invoke({"review": REVIEW})

    print("--- Exercise 1: 4-branch parallel enrichment ---")
    print("Sentiment: ", result["sentiment"])
    print("Summary:   ", result["summary"])
    print("Categories:", result["categories"])


class ReplyWithPriority(BaseModel):
    reply: str = Field(description="Draft customer service reply")
    priority: str = Field(description="One of: high, medium, low")


def exercise_2():
    """Final stage also outputs a priority field via structured output."""
    llm = get_chat_model()
    enrich = RunnablePassthrough.assign(sentiment=_sentiment_chain(llm), summary=_summary_chain(llm))

    structured_llm = llm.with_structured_output(ReplyWithPriority)
    reply_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "human",
                "Draft a reply and assign a priority.\n\nReview: {review}\nSentiment: {sentiment}\nSummary: {summary}",
            )
        ]
    )
    reply_chain = reply_prompt | structured_llm

    pipeline = enrich | reply_chain
    result = pipeline.invoke({"review": REVIEW})

    print("\n--- Exercise 2: reply + priority ---")
    print(result)


def exercise_3():
    """Measure RunnableParallel vs two sequential .invoke() calls."""
    llm = get_chat_model()
    sentiment_chain = _sentiment_chain(llm)
    summary_chain = _summary_chain(llm)
    parallel = RunnableParallel(sentiment=sentiment_chain, summary=summary_chain)

    start = time.perf_counter()
    parallel.invoke({"review": REVIEW})
    parallel_time = time.perf_counter() - start

    start = time.perf_counter()
    sentiment_chain.invoke({"review": REVIEW})
    summary_chain.invoke({"review": REVIEW})
    sequential_time = time.perf_counter() - start

    print("\n--- Exercise 3: parallel vs sequential timing ---")
    print(f"RunnableParallel: {parallel_time:.2f}s")
    print(f"Sequential calls: {sequential_time:.2f}s")


def exercise_4():
    """Batch 3 reviews through the full pipeline, print a table."""
    llm = get_chat_model()
    enrich = RunnablePassthrough.assign(sentiment=_sentiment_chain(llm), summary=_summary_chain(llm))
    reply_chain = (
        ChatPromptTemplate.from_messages(
            [("human", "Draft a short reply.\n\nReview: {review}\nSentiment: {sentiment}")]
        )
        | llm
        | StrOutputParser()
    )
    pipeline = enrich | RunnableParallel(
        review=lambda x: x["review"],
        sentiment=lambda x: x["sentiment"],
        reply=reply_chain,
    )

    reviews = [
        {"review": "Great product, fast shipping, will buy again!"},
        {"review": "Terrible experience, item arrived broken."},
        {"review": "It's fine, does what it says, nothing special."},
    ]
    results = pipeline.batch(reviews)

    print("\n--- Exercise 4: batch table ---")
    for r in results:
        print(f"{r['sentiment']:<10} | {r['review'][:40]:<40} | {r['reply'][:60]}")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()

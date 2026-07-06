"""
Module 05 - Sequential Chain (multi-input/output via RunnableParallel + .assign()).

Run: python modules/05_sequential_chain/example.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from common.model_factory import get_chat_model

REVIEW = (
    "The headphones arrived two days late and the box was dented, but honestly the "
    "sound quality is fantastic and the noise cancelling is better than my old pair."
)


def build_pipeline():
    llm = get_chat_model()

    sentiment_chain = (
        ChatPromptTemplate.from_messages(
            [("human", "In one word (positive/negative/mixed), what is the sentiment of:\n\n{review}")]
        )
        | llm
        | StrOutputParser()
    )

    summary_chain = (
        ChatPromptTemplate.from_messages(
            [("human", "Summarize this review in one sentence:\n\n{review}")]
        )
        | llm
        | StrOutputParser()
    )

    # Stage 1: keep the original review, and compute sentiment + summary alongside it, in parallel.
    enrich = RunnablePassthrough.assign(
        sentiment=sentiment_chain,
        summary=summary_chain,
    )

    # Stage 2: a reply drafter that genuinely needs all three fields at once.
    reply_chain = (
        ChatPromptTemplate.from_messages(
            [
                (
                    "human",
                    "Draft a short customer-service reply.\n\n"
                    "Original review: {review}\n"
                    "Detected sentiment: {sentiment}\n"
                    "Summary: {summary}\n\n"
                    "The reply should acknowledge the specific summary point and match the sentiment.",
                )
            ]
        )
        | llm
        | StrOutputParser()
    )

    return enrich | RunnableParallel(
        review=lambda x: x["review"],
        sentiment=lambda x: x["sentiment"],
        summary=lambda x: x["summary"],
        reply=reply_chain,
    )


if __name__ == "__main__":
    pipeline = build_pipeline()
    result = pipeline.invoke({"review": REVIEW})

    print("--- Sequential chain result ---")
    print("Sentiment:", result["sentiment"])
    print("Summary:  ", result["summary"])
    print("Reply:    ", result["reply"])

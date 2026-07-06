"""
Module 02 - Prompt Templates.

Run: python modules/02_prompt_templates/example.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

from common.model_factory import get_chat_model


def basic_template():
    llm = get_chat_model()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful translator. Only output the translation, nothing else."),
            ("human", "Translate '{text}' into {language}."),
        ]
    )
    chain = prompt | llm
    response = chain.invoke({"text": "Good morning", "language": "French"})
    print("--- Basic template ---")
    print(response.content)


def partial_template():
    llm = get_chat_model()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You always answer as {persona}."),
            ("human", "{question}"),
        ]
    )
    pirate_prompt = prompt.partial(persona="a friendly pirate")
    chain = pirate_prompt | llm
    response = chain.invoke({"question": "How do I reverse a list in Python?"})
    print("\n--- Partial template ---")
    print(response.content)


def few_shot_template():
    llm = get_chat_model()
    examples = [
        {"input": "I love this product, it works perfectly!", "output": "sentiment: positive"},
        {"input": "This is the worst purchase I've made all year.", "output": "sentiment: negative"},
        {"input": "It arrived on time, nothing special.", "output": "sentiment: neutral"},
    ]
    example_prompt = ChatPromptTemplate.from_messages([("human", "{input}"), ("ai", "{output}")])
    few_shot = FewShotChatMessagePromptTemplate(example_prompt=example_prompt, examples=examples)

    final_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Classify sentiment. Respond only in the format 'sentiment: <label>'."),
            few_shot,
            ("human", "{input}"),
        ]
    )
    chain = final_prompt | llm
    response = chain.invoke({"input": "Shipping took three weeks and the box was crushed."})
    print("\n--- Few-shot template ---")
    print(response.content)


if __name__ == "__main__":
    basic_template()
    partial_template()
    few_shot_template()

"""
Module 02 - Exercise solutions.

Run: python modules/02_prompt_templates/solutions.py
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

from common.model_factory import get_chat_model


def exercise_1():
    """Add a {tone} variable to the system message, test formal vs sarcastic."""
    llm = get_chat_model()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Answer in a {tone} tone."),
            ("human", "{question}"),
        ]
    )
    chain = prompt | llm

    print("--- Exercise 1: tone variable ---")
    for tone in ["formal", "sarcastic"]:
        response = chain.invoke({"tone": tone, "question": "Should I use a virtual environment?"})
        print(f"[{tone}] {response.content}\n")


def exercise_2():
    """5-example few-shot classifier: bug / feature-request / question."""
    llm = get_chat_model()
    examples = [
        {"input": "The app crashes when I click submit.", "output": "bug"},
        {"input": "Can you add dark mode?", "output": "feature-request"},
        {"input": "How do I reset my password?", "output": "question"},
        {"input": "Export to CSV throws a 500 error.", "output": "bug"},
        {"input": "It would be great to have keyboard shortcuts.", "output": "feature-request"},
    ]
    example_prompt = ChatPromptTemplate.from_messages([("human", "{input}"), ("ai", "{output}")])
    few_shot = FewShotChatMessagePromptTemplate(example_prompt=example_prompt, examples=examples)
    final_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Classify the support ticket. Respond with exactly one label: bug, feature-request, or question."),
            few_shot,
            ("human", "{input}"),
        ]
    )
    chain = final_prompt | llm

    print("--- Exercise 2: ticket classification ---")
    for ticket in [
        "The page takes 30 seconds to load.",
        "Could you support SSO login?",
        "What plans include API access?",
    ]:
        response = chain.invoke({"input": ticket})
        print(f"{ticket!r} -> {response.content}")


def exercise_3():
    """.partial() to bake in current_date, confirm the model can answer correctly."""
    llm = get_chat_model()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Today's date is {current_date}."),
            ("human", "{question}"),
        ]
    )
    dated_prompt = prompt.partial(current_date=datetime.now().strftime("%Y-%m-%d"))
    chain = dated_prompt | llm

    print("\n--- Exercise 3: partial current_date ---")
    response = chain.invoke({"question": "What is today's date?"})
    print(response.content)


def exercise_4():
    """Serialize a ChatPromptTemplate (via pickle, the most reliable round-trip
    for arbitrary LangChain objects) and reload it, confirm identical output."""
    import pickle

    prompt = ChatPromptTemplate.from_messages([("human", "Say hello to {name}.")])

    serialized = pickle.dumps(prompt)
    reloaded = pickle.loads(serialized)

    original_output = prompt.invoke({"name": "Alice"})
    reloaded_output = reloaded.invoke({"name": "Alice"})

    print("\n--- Exercise 4: serialize / reload ---")
    print("Original:", original_output)
    print("Reloaded:", reloaded_output)
    print("Identical:", original_output == reloaded_output)


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()

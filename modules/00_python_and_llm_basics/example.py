"""
Module 00 - Python basics warm-up. No API key required -- everything here runs offline.

Run: python modules/00_python_and_llm_basics/example.py
"""

import asyncio


def fstring_and_types_demo():
    name = "Claude"
    greeting = f"Hello, {name}!"
    print("--- f-strings ---")
    print(greeting)


def dict_and_list_comprehension_demo():
    print("\n--- dicts and list comprehensions ---")
    config = {"provider": "anthropic", "temperature": 0.7}
    print("config:", config)
    print("temperature:", config["temperature"])

    documents = ["doc1", "doc22", "doc333"]
    lengths = [len(doc) for doc in documents]
    print("documents:", documents)
    print("lengths:  ", lengths)


class Greeter:
    """A tiny stand-in for the kind of object LangChain hands you everywhere (e.g. a chat model)."""

    def __init__(self, name: str):
        self.name = name

    def invoke(self, message: str) -> str:
        return f"{self.name} says: {message}"


def class_demo():
    print("\n--- classes and methods ---")
    greeter = Greeter(name="Assistant")
    print(greeter.invoke("hello there"))


def shout(func):
    """A decorator: wraps func so its string return value comes back uppercased."""

    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result.upper()

    return wrapper


@shout
def say_hello() -> str:
    return "hello world"


def decorator_demo():
    print("\n--- decorators ---")
    print(say_hello())


async def wait_and_greet():
    await asyncio.sleep(0.1)  # stands in for "waiting on a slow network call"
    return "done waiting"


async def async_demo():
    print("\n--- async/await ---")
    result = await wait_and_greet()
    print(result)


if __name__ == "__main__":
    fstring_and_types_demo()
    dict_and_list_comprehension_demo()
    class_demo()
    decorator_demo()
    asyncio.run(async_demo())

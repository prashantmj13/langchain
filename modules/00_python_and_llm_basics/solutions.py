"""
Module 00 - Exercise solutions. No API key required.

Run: python modules/00_python_and_llm_basics/solutions.py
"""

import asyncio


def exercise_1():
    """Write describe(name, age=0) -> str, call it with and without age."""

    def describe(name: str, age: int = 0) -> str:
        return f"{name} is {age} years old"

    print("--- Exercise 1 ---")
    print(describe("Alice"))
    print(describe("Bob", 30))


def exercise_2():
    """List comprehension: fruit names costing more than $1."""
    prices = {"apple": 1.5, "banana": 0.5, "cherry": 3.0}
    expensive = [fruit for fruit, price in prices.items() if price > 1]

    print("\n--- Exercise 2 ---")
    print(expensive)


def exercise_3():
    """A @shout decorator that uppercases a wrapped function's string return value."""

    def shout(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs).upper()

        return wrapper

    @shout
    def greet() -> str:
        return "hello world"

    print("\n--- Exercise 3 ---")
    print(greet())


async def _exercise_4_coro():
    await asyncio.sleep(1)
    print("done")


def exercise_4():
    """An async function that sleeps 1s then prints 'done'."""
    print("\n--- Exercise 4 ---")
    asyncio.run(_exercise_4_coro())


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()

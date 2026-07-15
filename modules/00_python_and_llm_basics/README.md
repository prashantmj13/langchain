# 00 — Python & LLM Basics (start here if you're new)

If you already know Python and have called an LLM API before, skip straight to [module 01](../01_langchain_basics). If either of those is new to you, read this first — every later module assumes the concepts below.

## Part 1: Python concepts this repo leans on

You don't need to be a Python expert, but you'll see these constructs constantly. Here's the minimum vocabulary.

### Variables, f-strings, and type hints
```python
name = "Claude"                          # a variable
greeting = f"Hello, {name}!"             # an f-string: {expr} is substituted into the string
def greet(name: str) -> str:             # "name: str" and "-> str" are type hints:
    return f"Hello, {name}!"             # documentation for humans and tools, not enforced at runtime
```
Type hints don't change how the code runs — Python doesn't check them by default — but LangChain *reads* them to build tool schemas ([module 19](../19_agents)) and MCP servers use them to describe tool arguments to the model ([module 21](../21_mcp_create_server)). Get in the habit of writing them.

### Lists, dicts, and comprehensions
```python
documents = ["doc1", "doc2", "doc3"]              # a list: ordered, indexed from 0
config = {"provider": "anthropic", "temperature": 0.7}   # a dict: key -> value lookup
config["temperature"]                              # 0.7

# A list comprehension: build a new list by transforming each element
lengths = [len(doc) for doc in documents]          # [4, 4, 4]
```
LangChain messages, retrieved documents, and embeddings are almost always passed around as lists or dicts.

### Functions with default arguments
```python
def get_chat_model(provider: str = "anthropic", temperature: float = 0.7):
    ...
```
`provider="anthropic"` is a default — callers can omit it (`get_chat_model()`) or override it (`get_chat_model(provider="openai")`). This exact pattern is [`common/model_factory.py`](../../common/model_factory.py), the function nearly every module in this repo imports.

### Classes and objects (just enough to read LangChain code)
```python
class ChatAnthropic:
    def __init__(self, model: str, temperature: float = 0.7):
        self.model = model
        self.temperature = temperature

    def invoke(self, messages):
        ...  # calls the Anthropic API and returns a response object

llm = ChatAnthropic(model="claude-sonnet-4-5")   # create an "instance" of the class
llm.invoke([...])                                 # call a "method" on it
```
You'll never write a class like this yourself in this repo — but every model, prompt template, and vector store you use *is* an object like this, and `.invoke(...)` is the one method almost all of them share (see [module 01](../01_langchain_basics)).

### Decorators (`@something`)
```python
@tool
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b
```
A decorator wraps a function to add behavior without changing its body. `@tool` (used in [module 19](../19_agents)) turns a plain function into something a LangChain agent can call; `@mcp.tool()` (module 21) does the same for MCP; `@traceable` (module 27) makes a function show up in LangSmith. You use decorators by putting `@name` directly above a function definition — that's it.

### `async`/`await` (used in the MCP modules)
```python
async def main():
    result = await session.call_tool("get_weather", {"city": "Tokyo"})
    print(result)

asyncio.run(main())
```
Regular Python runs one thing at a time and waits. `async`/`await` lets a program start a slow operation (like a network call) and let other work happen while it waits, instead of blocking. You mark a function `async def`, and inside it you `await` anything that's itself async. Modules [22](../22_mcp_stdio_client)-[26](../26_mcp_implement_client) (MCP) use this because talking to a server over a socket/pipe is exactly this kind of "wait for a response" operation. Everywhere else in this repo, plain synchronous `.invoke()` is used instead — you don't need `async` for the majority of the repo.

### Context managers (`with`)
```python
with open("file.txt") as f:
    contents = f.read()
# file is automatically closed here, even if an error happened above
```
`with` (and its async cousin `async with`, used in the MCP client modules) guarantees setup/cleanup happens correctly — opening and closing a file, or opening and closing a connection to an MCP server.

### Virtual environments, `pip`, and `.env` files
- A **virtual environment** (`.venv`) is an isolated Python installation for one project, so its dependencies don't collide with any other project's. You create one with `python -m venv .venv` and "activate" it before installing anything.
- `pip install -r requirements.txt` installs every package listed in that file into the currently active environment.
- A **`.env` file** holds secrets (API keys) as `KEY=value` lines, kept out of git (see `.gitignore`) so you never accidentally commit a credential. `python-dotenv`'s `load_dotenv()` reads it into environment variables at startup, which `os.getenv("ANTHROPIC_API_KEY")` then reads.

### JSON
```python
{"role": "human", "content": "Hello"}
```
JSON is the universal format LLM APIs speak: your messages get serialized to JSON to send over HTTP, and API responses come back as JSON. Python dicts and JSON look almost identical on purpose — `json.dumps(a_dict)` converts one to the other.

## Part 2: LLM/API concepts this repo leans on

- **LLM (Large Language Model)** — a model trained on huge amounts of text that predicts the most likely next tokens given some input. Claude, GPT-4, and Gemini are all LLMs, accessed through an API rather than run on your own machine.
- **Token** — the unit an LLM actually processes; roughly 3/4 of a word on average in English. Pricing, context limits, and speed are all measured in tokens, not characters or words.
- **Prompt** — the text (and, for chat models, the list of role-tagged messages) you send the model. "Prompt engineering" just means writing/structuring that input carefully to get better output.
- **API key** — a secret credential that authenticates your requests to a provider (Anthropic, OpenAI, ...) and is how usage gets billed to your account. Treat it like a password: never commit it to git, never paste it into a public chat.
- **SDK / client library** — `anthropic`, `langchain-anthropic`, `openai`, etc. are Python packages that wrap the underlying HTTP API so you call a normal Python function (`llm.invoke(...)`) instead of manually constructing HTTP requests and parsing JSON responses yourself.
- **System prompt vs. user message** — most chat APIs let you set a `system` message that steers the model's overall behavior/persona, separate from the actual conversation (`human`/`user` and `assistant`/`ai` messages). See [module 01](../01_langchain_basics).
- **Temperature** — a number (usually 0-1) controlling how deterministic vs. varied the model's output is. Low temperature (0-0.3): more focused/repeatable. High temperature (0.7-1.0): more varied/creative.
- **Context window** — the maximum number of tokens (input + output combined) a model can handle in one call. This is *why* techniques like RAG ([module 16](../16_rag)) exist: you can't just paste an entire knowledge base into every prompt.
- **Rate limits & cost** — API providers cap how many requests/tokens you can send per minute, and charge per token (input and output are usually priced differently, output costs more). Keep this in mind before writing a loop that calls an LLM thousands of times.

## Use Case

This module has no "use case" of its own — it's the shared vocabulary the rest of the repo assumes you have.

## How to Run

```bash
python modules/00_python_and_llm_basics/example.py
python modules/00_python_and_llm_basics/solutions.py   # exercise solutions
```
No API key needed — everything in this module runs offline. Each script executes top to bottom and prints one labeled section per concept (`--- f-strings ---`, `--- decorators ---`, etc.) as it goes.

## Walkthrough

`example.py` is a short, dependency-free (no API key needed) script that exercises the Python constructs above in isolation — f-strings, a dict, a list comprehension, a class with a method, a decorator, and an `async` function — so you can run it, read it, and confirm you understand each piece before module 01 puts them to work against a real model.

## Reference Docs

- Official Python tutorial: https://docs.python.org/3/tutorial/
- Real Python's guide to `async`/`await`: https://realpython.com/async-io-python/
- Anthropic's "Getting started" guide: https://docs.anthropic.com/en/docs/get-started
- What is a token (Anthropic): https://docs.anthropic.com/en/docs/resources/glossary

## Exercises

Each exercise below targets one of the "Part 1" concepts above — do them in order, since later ones assume you're comfortable with the earlier ones.

1. **Default arguments** (the pattern `get_chat_model()` uses everywhere). Write a function `describe(name: str, age: int = 0) -> str` that returns the f-string `f"{name} is {age} years old"`. Then call it twice: once as `describe("Alice")` (relying on the default `age=0`) and once as `describe("Bob", 30)` (overriding it). Confirm both calls print sensible output — that's the whole point of a default: the caller can supply it or skip it.
2. **List comprehensions over a dict** (the pattern used to filter/transform search results throughout this repo). Given `prices = {"apple": 1.5, "banana": 0.5, "cherry": 3.0}`, write a single list comprehension that returns only the fruit *names* (not the prices) where the price is greater than $1 — expected result: `["apple", "cherry"]`. You'll need `.items()` to loop over both the key and value at once, plus an `if` condition inside the comprehension.
3. **Decorators** (the mechanism behind `@tool` in module 19 and `@mcp.tool()` in module 21). Write a decorator named `@shout` that takes whatever string a wrapped function returns and converts it to uppercase before returning it. Apply it to a function that returns `"hello world"`, and confirm calling that function now returns `"HELLO WORLD"` instead.
4. **`async`/`await`** (the mechanism every MCP client in this repo uses). Write an `async def` function that does two things in order: `await asyncio.sleep(1)` (simulating a 1-second wait, like a network call), then `print("done")`. Run it with `asyncio.run(your_function())` at the bottom of your script, and confirm there's a visible ~1 second pause before `"done"` prints.

**Solutions:** see [`solutions.py`](solutions.py) in this folder.

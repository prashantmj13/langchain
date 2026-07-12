# 07 — Chat History

## Theory

A chat model call is stateless — Claude has no memory of your previous message unless you send the entire conversation back every time. LangChain formalizes this with:

- **`BaseChatMessageHistory`** — a store (in-memory, Redis, SQL, etc.) of messages keyed by a `session_id`.
- **`RunnableWithMessageHistory`** — wraps any chain and automatically (1) loads prior messages for a session, (2) injects them into the prompt, (3) appends the new human/AI turn back into the store after each call.
- **Session scoping** — every call carries a `configurable={"session_id": "..."}`, so one process can hold many independent conversations (e.g. one per logged-in user) without them bleeding into each other.

## Use Case

Any multi-turn chatbot or assistant. Without this, "what did I just ask you?" always fails — the model has zero context beyond the single message it was just sent.

## How to Run

```bash
python modules/07_chat_history/example.py
python modules/07_chat_history/solutions.py   # exercise solutions
```
Requires `ANTHROPIC_API_KEY` in `.env`. The `_store` dict lives only in the running process's memory — history resets every time you re-run the script. Watch the third question in Alice's session ("What did I just ask you?") to confirm history is actually being carried between calls.

## Walkthrough

`example.py`:
1. Builds a chain (`ChatPromptTemplate` with a `MessagesPlaceholder` + Claude).
2. Wraps it in `RunnableWithMessageHistory` backed by an in-memory store keyed by `session_id`.
3. Runs a 3-turn conversation in session `"alice"` where the third question ("What did I just ask?") only works because history is being carried.
4. Starts a second, independent session `"bob"` to prove sessions don't leak into each other.

## Using a different model

Chat history management is entirely model-agnostic — `RunnableWithMessageHistory` wraps whatever chain you give it, Claude or otherwise. Swap the model inside the wrapped chain exactly as in [module 01](../01_langchain_basics).

## Reference Docs

- Message history how-to: https://python.langchain.com/docs/how_to/message_history/
- `RunnableWithMessageHistory` API: https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.history.RunnableWithMessageHistory.html
- `MessagesPlaceholder`: https://python.langchain.com/api_reference/core/prompts/langchain_core.prompts.chat.MessagesPlaceholder.html

## Exercises

1. Add a 4th turn to Alice's session asking her to summarize the whole conversation so far.
2. Cap history to the last 6 messages (trim older ones) so token usage doesn't grow unbounded in a long conversation -- use `trim_messages`.
3. Swap the in-memory store for a JSON-file-backed store that persists across process restarts.
4. Run two sessions concurrently (interleaved calls) and confirm Alice's and Bob's histories never cross-contaminate.

**Solutions:** see [`solutions.py`](solutions.py) in this folder.

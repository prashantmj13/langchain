# 07 — Chat History

## Theory

Claude doesn't remember anything between calls — every single `.invoke()` starts completely fresh. If it seems to "remember" what you said earlier, that's an illusion *you* create by re-sending the whole conversation so far, every single time. LangChain gives you tools to manage that instead of doing it by hand:

- **A place to store the conversation.** Something needs to hold onto the growing list of messages between calls — it could just be a Python list in memory, or something more durable like a database. LangChain calls this a "message history," and each one is labeled with a `session_id` so you can tell different conversations apart.
- **Automating the "load, add, save" cycle.** Instead of manually fetching the old messages, adding them to your prompt, calling the model, and saving the new messages back — `RunnableWithMessageHistory` wraps a chain and does all three steps for you, every time you call it.
- **Keeping conversations separate.** By passing a different `session_id` for each user (or each conversation), one running program can juggle many completely independent conversations at once without them getting mixed up.

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

## Classes & Methods Used

| API | What It Does | Why We Use It Here |
|---|---|---|
| `ChatMessageHistory` | A simple, in-memory list of messages for one conversation. | Used as the actual storage for each session's message list — the thing `get_session_history()` creates/returns per `session_id`. |
| `MessagesPlaceholder(variable_name="history")` | A spot inside a `ChatPromptTemplate` that gets filled in with a whole list of prior messages, not just one value. | Used so the prompt template has a place to insert the growing conversation history before the new question. |
| `RunnableWithMessageHistory(chain, get_session_history, ...)` | Wraps a chain so that, on every call, it automatically loads that session's history, injects it via the placeholder above, and saves the new turn back afterward. | This is the whole point of the module — it's what turns a stateless chain into something that remembers a conversation, without you manually managing the message list. |
| `config={"configurable": {"session_id": "alice"}}` | A per-call setting telling `RunnableWithMessageHistory` which session's history to load/save. | Used to keep Alice's and Bob's conversations separate even though they're going through the same chain object. |

## Using a different model

Chat history management is entirely model-agnostic — `RunnableWithMessageHistory` wraps whatever chain you give it, Claude or otherwise. Swap the model inside the wrapped chain exactly as in [module 01](../01_langchain_basics).

## Reference Docs

- Message history how-to: https://python.langchain.com/docs/how_to/message_history/
- `RunnableWithMessageHistory` API: https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.history.RunnableWithMessageHistory.html
- `MessagesPlaceholder`: https://python.langchain.com/api_reference/core/prompts/langchain_core.prompts.chat.MessagesPlaceholder.html

## Exercises

1. **A 4th turn that specifically tests memory.** `example.py`'s Alice session already has 3 turns, ending with "What did I just ask you about?" Add a 4th call asking "Summarize our conversation so far in 2 sentences" — this is a stronger test than turn 3, since it requires the model to actually recall *all* prior turns, not just the most recent one.
2. **Preventing history from growing forever.** In a long-running chat, sending the entire history on every call gets expensive and eventually hits the context window limit (module 00's glossary). `trim_messages` (from `langchain_core.messages.utils`) can cut a message list down to the last N — build a `ChatMessageHistory` with 10+ messages in it, then call `trim_messages(history.messages, max_tokens=6, strategy="last", token_counter=len)` and confirm you get back only the last 6.
3. **Persisting history across process restarts.** `example.py`'s `_store` dict lives only in memory — it's gone the moment the script ends. Write a small class implementing `BaseChatMessageHistory` (subclass it, and implement `.messages`, `.add_message()`, `.clear()`) that reads/writes to a JSON file on disk instead of a Python dict. Confirm history survives: run your script, add some messages, then run it again and see the earlier messages still there.
4. **Confirming sessions genuinely don't leak into each other under concurrency.** Using Python's `threading` module, start two threads that each send a message to a *different* `session_id` at roughly the same time. After both finish, check that Alice's history contains no trace of Bob's message and vice versa — this matters because a real multi-user app will have exactly this kind of concurrent access.

**Solutions:** see [`solutions.py`](solutions.py) in this folder.

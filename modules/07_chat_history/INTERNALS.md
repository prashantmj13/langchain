# Module 07 — Internals

## `RunnableWithMessageHistory`

**What it is:** A wrapper `Runnable` that sits around your actual chain and handles the "load history, run the chain, save the new turn" cycle automatically on every call.

**How it works internally:**
1. When you build it (`RunnableWithMessageHistory(chain, get_session_history, input_messages_key="input", history_messages_key="history")`), it just stores a reference to your chain and your `get_session_history` function — no history is loaded yet.
2. On `.invoke({"input": "..."}, config={"configurable": {"session_id": "alice"}})`, it first reads `session_id` out of the `config` dict and calls `get_session_history("alice")` to fetch (or create) that session's `BaseChatMessageHistory`.
3. It reads the **current** `.messages` list off that history object and inserts it wherever your prompt template's `MessagesPlaceholder(variable_name="history")` is — this is why the `history_messages_key` you pass in must exactly match the `variable_name` in your prompt.
4. It then calls your wrapped chain's `.invoke()` with the combined input (your new message plus the injected history).
5. After the chain returns, it takes your new input message *and* the chain's response, and appends both to the same history object via `.add_user_message()`/`.add_ai_message()` — so the next call to the same `session_id` will see this turn too.

**Real source:** [`langchain_core/runnables/history.py`](https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/runnables/history.py) — look for the `RunnableWithMessageHistory` class, and specifically its `_merge_configs`/`invoke` methods for the session-lookup logic.

**How to validate it's working:**
```python
chain_with_history = build_chain_with_history()
config = {"configurable": {"session_id": "test-session"}}

chain_with_history.invoke({"input": "My favorite color is blue."}, config=config)
history = get_session_history("test-session")
print(len(history.messages))   # 2 -- your message + the model's reply, both saved automatically

response = chain_with_history.invoke({"input": "What's my favorite color?"}, config=config)
print(response.content)        # should correctly say "blue" -- proof history was actually loaded and used
print(len(history.messages))   # 4 now -- 2 more messages appended
```

## `ChatMessageHistory`

**What it is:** The simplest implementation of `BaseChatMessageHistory` — just a Python list of messages wrapped with a few convenience methods.

**How it works internally:** `.add_user_message(text)` is a shortcut for `self.messages.append(HumanMessage(content=text))`; `.add_ai_message(text)` does the same with `AIMessage`. `.messages` is a plain Python list attribute — there's no database, no file, nothing persisted; the moment the Python object is garbage-collected (e.g. your script ends), the history is gone. That's exactly why `example.py`'s `_store` dict has to keep a reference to each session's `ChatMessageHistory` object alive for the whole run.

**Real source:** [`langchain_community/chat_message_histories/in_memory.py`](https://github.com/langchain-ai/langchain/blob/master/libs/community/langchain_community/chat_message_histories/in_memory.py).

**How to validate it's working:**
```python
history = ChatMessageHistory()
history.add_user_message("hi")
history.add_ai_message("hello!")
print(history.messages)   # [HumanMessage(content='hi'), AIMessage(content='hello!')]
```

## `MessagesPlaceholder(variable_name="history")`

**What it is:** A special entry inside a `ChatPromptTemplate.from_messages([...])` list that reserves a spot for a *whole list* of messages, not a single templated string.

**How it works internally:** Every other entry in a `ChatPromptTemplate`'s message list renders to exactly one message. `MessagesPlaceholder` is different — when the template is invoked with `{"history": [msg1, msg2, ...]}`, it expands to however many messages are in that list, inserted in order at that exact position in the final message sequence. This is what lets a variable-length conversation history slot into a fixed-shape prompt template.

**Real source:** [`langchain_core/prompts/chat.py`](https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/prompts/chat.py) — look for the `MessagesPlaceholder` class.

**How to validate it's working:**
```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are helpful."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])
rendered = prompt.invoke({"history": [HumanMessage(content="earlier msg"), AIMessage(content="earlier reply")], "input": "new question"})
print(len(rendered.to_messages()))  # 4: system + 2 history messages + the new human message
```

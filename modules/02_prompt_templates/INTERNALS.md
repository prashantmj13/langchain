# Module 02 — Internals

## `ChatPromptTemplate`

**What it is:** A `Runnable` (module 03) that turns a list of `(role, template_string)` pairs into a real list of messages, substituting in whatever values you pass to `.invoke()`.

**How it works internally:**
1. `.from_messages([("system", "..."), ("human", "{question}")])` scans each template string for `{name}` placeholders using Python's own string-formatting syntax, and records which variable names it needs (`input_variables`).
2. It doesn't render anything yet at this point — same "build now, run later" pattern as every other `Runnable` (see module 03's Execution Internals).
3. When you call `.invoke({"question": "..."})`, it loops through its stored `(role, template)` pairs, calls Python's `str.format(**your_dict)` on each template string, and wraps the result in the matching message class (`"system"` → `SystemMessage`, `"human"` → `HumanMessage`).
4. It returns a `ChatPromptValue` object — which behaves like a list of messages (so it can be handed straight to a chat model's `.invoke()`) but also keeps the original template around for introspection.

**Real source:** [`langchain_core/prompts/chat.py`](https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/prompts/chat.py) — look for `ChatPromptTemplate` and `from_messages`.

**How to validate it's working:**
```python
prompt = ChatPromptTemplate.from_messages([("human", "Say hi to {name}")])
result = prompt.invoke({"name": "Alice"})
print(result.to_messages())    # [HumanMessage(content='Say hi to Alice')]
```
If you pass a dict missing a required key (e.g. `.invoke({})` when the template needs `{name}`), you'll get a `KeyError` — that's the template telling you exactly which variable you forgot.

## `.partial(persona="...")`

**What it is:** A method that returns a *new* `ChatPromptTemplate` with one or more variables already filled in, leaving the rest for later.

**How it works internally:** It doesn't modify the original template (Runnables are meant to be treated as immutable) — it creates a copy whose `input_variables` list has the partial'd names removed, and stores your supplied values separately. When `.invoke()` is later called on the *new* template, it merges your partial values with whatever you pass in at call time before formatting.

**Real source:** Same file as above — `ChatPromptTemplate.partial()` is inherited from the shared `BasePromptTemplate` in [`langchain_core/prompts/base.py`](https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/prompts/base.py).

**How to validate it's working:**
```python
prompt = ChatPromptTemplate.from_messages([("system", "You are {persona}."), ("human", "{q}")])
print(prompt.input_variables)              # ['persona', 'q']

partial_prompt = prompt.partial(persona="a pirate")
print(partial_prompt.input_variables)      # ['q'] -- 'persona' is gone, it's already filled in
```

## `FewShotChatMessagePromptTemplate`

**What it is:** A prompt template that, instead of one fixed template, renders a *list* of examples (each through its own small `example_prompt` template) and inserts all of them into the final message list before your real question.

**How it works internally:**
1. You give it an `example_prompt` (a mini `ChatPromptTemplate`, usually `[("human", "{input}"), ("ai", "{output}")]`) and a list of example dicts.
2. On `.invoke()`, it loops over every example, renders each one through `example_prompt`, and concatenates all the resulting messages together, in order.
3. When you embed it inside a larger `ChatPromptTemplate.from_messages([system, few_shot, ("human", "{input}")])`, it slots its whole rendered example-message-list in at that position — so the model sees: system instruction, then every example as if it were a real back-and-forth conversation, then your actual question.

**Real source:** [`langchain_core/prompts/few_shot.py`](https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/prompts/few_shot.py).

**How to validate it's working:**
```python
rendered = few_shot.format_messages()   # or inspect via the full prompt's .invoke(...).to_messages()
print(len(rendered))   # should be 2x your number of examples (one human + one ai message per example)
```
If the model isn't following your intended output format, the first thing to check is whether the examples actually rendered correctly — print them and read them the way the model will see them.

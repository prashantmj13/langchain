# Module 17 — Internals

`create_stuff_documents_chain`, `create_retrieval_chain`, `MessagesPlaceholder`, and `RunnableWithMessageHistory` are all covered in [module 14's](../14_retrieval/INTERNALS.md) and [module 07's](../07_chat_history/INTERNALS.md) INTERNALS.md pages. This module's one new piece is the history-aware retriever wrapper.

## `create_history_aware_retriever(llm, retriever, contextualize_prompt)`

**What it is:** A helper that wraps a plain retriever with an extra LLM call that runs *before* the actual search — rewriting the incoming question into a standalone one, using chat history.

**How it works internally:**
1. It builds a small internal chain: `contextualize_prompt | llm | StrOutputParser()` — using your `contextualize_prompt` (the one instructing the model to rewrite follow-ups), the same `llm` you passed in, and a plain string parser (module 03).
2. It returns a new `Runnable` whose `.invoke({"input": ..., "chat_history": [...]})` does two things in sequence: first, if `chat_history` is empty (the very first question in a conversation), it skips the rewriting step entirely and searches with the original `input` directly — there's nothing to rewrite yet. Second, if there *is* history, it runs the rewriting chain first, takes its output (the standalone question), and passes *that* to the wrapped retriever's `.invoke()` instead of the original input.
3. The result is a drop-in replacement for a plain retriever — from `create_retrieval_chain`'s point of view (module 14), it doesn't matter whether the retriever it's wired to is a plain one or a history-aware one; both just implement `.invoke(input) -> list[Document]`.

**Real source:** [`langchain/chains/history_aware_retriever.py`](https://github.com/langchain-ai/langchain/blob/master/libs/langchain/langchain/chains/history_aware_retriever.py).

**How to validate the rewriting step is genuinely happening:**
```python
llm = get_chat_model()
retriever = build_retriever()
history_aware_retriever, contextualize_prompt = _build_history_aware_retriever(llm, retriever)

# First question: no history, should search with the literal input
result_1 = history_aware_retriever.invoke({"input": "How many PTO days do employees get?", "chat_history": []})
print(len(result_1))  # some retrieved documents

# Follow-up: with history, the vague "that" should get resolved before searching
from langchain_core.messages import HumanMessage, AIMessage
history = [HumanMessage(content="How many PTO days do employees get?"), AIMessage(content="15 days per year.")]
result_2 = history_aware_retriever.invoke({"input": "How much of that carries over?", "chat_history": history})
print(len(result_2))
# Confirm result_2 actually found PTO-related chunks (print their content) even though
# "How much of that carries over?" alone shares almost no words with the handbook text about PTO
```
If you want to see the *rewritten question itself*, not just its effect on search results, build the `contextualize_prompt | llm` chain separately and call `.invoke()` on it directly — see exercise 1.

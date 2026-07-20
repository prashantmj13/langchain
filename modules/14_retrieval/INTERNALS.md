# Module 14 — Internals

## `vector_store.as_retriever()`

**What it is:** A method every vector store has that returns a `VectorStoreRetriever` — a thin `Runnable` wrapper around the store, so it can be used inside `|` chains exactly like a model or a prompt.

**How it works internally:** `VectorStoreRetriever` stores a reference back to the vector store it was built from, plus your `search_type`/`search_kwargs` settings. Its `.invoke(query)` implementation is close to `return self.vectorstore.similarity_search(query, **self.search_kwargs)` (or `.max_marginal_relevance_search()`, if `search_type="mmr"`) — it doesn't do any searching itself, it just adapts the vector store's existing search methods to the standard `Runnable` interface (`.invoke()`/`.batch()`/`.stream()`) that module 03 covers.

**Real source:** [`langchain_core/vectorstores/base.py`](https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/vectorstores/base.py) — look for `VectorStoreRetriever`.

**How to validate it's working:**
```python
retriever = build_retriever()
print(isinstance(retriever, Runnable))   # True -- confirms it fits into | chains
results = retriever.invoke("How do I reduce duplicate results?")
print(type(results))    # <class 'list'> of Document objects, same as .similarity_search() returns directly
```

## `create_stuff_documents_chain(llm, prompt)`

**What it is:** A prebuilt helper that returns a `Runnable` implementing the "stuff all the retrieved documents into the prompt" pattern — "stuff" is the actual technical term LangChain uses for this strategy (as opposed to more complex strategies like "map-reduce" for when there are too many documents to fit in one prompt).

**How it works internally:**
1. It expects to be invoked with a dict containing a `"context"` key (a list of `Document`s) and whatever other keys your prompt template needs (e.g. `"input"`).
2. Internally, it formats every `Document` in `"context"` into a single block of text (by default, just joining each document's `page_content` with double newlines) and substitutes that combined text into your prompt template's `{context}` placeholder.
3. It then calls the LLM with the fully-assembled prompt and returns the response.

**Real source:** [`langchain/chains/combine_documents/stuff.py`](https://github.com/langchain-ai/langchain/blob/master/libs/langchain/langchain/chains/combine_documents/stuff.py) in the `langchain` (not `langchain-core`) package — this helper lives in the higher-level package, unlike the primitives from modules 01-03.

## `create_retrieval_chain(retriever, combine_docs_chain)`

**What it is:** Glue that wires a retriever and a combine-documents chain together into one pipeline, and standardizes the output shape.

**How it works internally:** It's conceptually equivalent to building `RunnablePassthrough.assign(context=retriever) | combine_docs_chain` (the same `.assign()` pattern from module 05) plus a bit of bookkeeping to also carry the retrieved `context` through into the final output dict (not just the generated `answer`) — which is exactly why `result["context"]` is available for you to inspect alongside `result["answer"]`.

**Real source:** [`langchain/chains/retrieval.py`](https://github.com/langchain-ai/langchain/blob/master/libs/langchain/langchain/chains/retrieval.py).

**How to validate the whole pipeline is genuinely using retrieval, not just the model's own knowledge:**
```python
result = retrieval_chain.invoke({"input": "What does create_retrieval_chain do?"})
print(result["answer"])
print("\nGrounded in:")
for doc in result["context"]:
    print("-", doc.page_content)
# Read the context and confirm every claim in the answer traces back to something in it --
# if the answer says something the context never mentioned, that's the model relying on its
# own training data instead of what was actually retrieved.
```

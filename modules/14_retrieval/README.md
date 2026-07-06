# 14 — Retrieval

## Theory

A **retriever** is LangChain's abstraction for "given a query string, return relevant `Document`s" — it's the interface that turns a vector store ([module 12](../12_vector_stores)) into something a chain can call with `.invoke(query)`, no different from any other `Runnable`.

- **`vector_store.as_retriever()`** — the most common retriever, backed by similarity or MMR search.
- **Search type & kwargs** — `search_type="similarity"` vs `"mmr"`, plus `k`, `score_threshold`, `fetch_k`.
- **`create_retrieval_chain`** — a prebuilt LangChain helper that wires a retriever and a "combine documents" chain together: it retrieves, stuffs the retrieved docs into a prompt, and calls the LLM, returning both the `answer` and the source `context` documents.
- **Retrievers are composable** — `MultiQueryRetriever` (generates several rephrased queries to widen recall), `ContextualCompressionRetriever` (re-ranks/trims retrieved docs before they reach the LLM) all wrap a base retriever with the same `Runnable` interface.

## Use Case

This is the "R" in RAG: any time an LLM needs facts beyond its training data or system prompt (your internal docs, a knowledge base, current data), you retrieve relevant context first, then generate. Retrieval is also useful standalone — e.g. "show me the 3 most relevant support articles" without ever calling an LLM.

## Walkthrough

`example.py`:
1. Builds a small Chroma vector store of documents (reusing the module 12 pattern).
2. Wraps it with `.as_retriever(search_type="similarity", k=2)` and calls `.invoke(query)` directly.
3. Builds a full `create_retrieval_chain` (retriever + Claude) and shows it returning both `answer` and `context`.
4. Compares `search_type="similarity"` vs `"mmr"` on a query with redundant documents.

## Using a different model

The retriever itself only depends on the embedding provider (via the underlying vector store); the "combine documents" / generation half of `create_retrieval_chain` uses whatever `get_chat_model(...)` you pass it.

## Reference Docs

- Retrieval concept: https://python.langchain.com/docs/concepts/retrievers/
- `create_retrieval_chain`: https://python.langchain.com/docs/how_to/qa_chat_history_how_to/
- `MultiQueryRetriever`: https://python.langchain.com/docs/how_to/MultiQueryRetriever/

## Exercises

1. Change `k` from 2 to 4 and observe how the retrieval chain's answer changes (more context, possibly more noise).
2. Add a `score_threshold` to the retriever and test a query that should return zero documents.
3. Wrap the base retriever with `MultiQueryRetriever.from_llm()` using Claude to generate query variations, and compare recall against the base retriever on a vaguely-worded query.
4. Print the `context` documents returned by `create_retrieval_chain` alongside the `answer` to verify the answer is actually grounded in them.

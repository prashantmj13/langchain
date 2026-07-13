# 14 — Retrieval

## Theory

A **retriever** is just "something you can ask a question, and it hands you back the documents that seem relevant." It's a thin wrapper around a vector store ([module 12](../12_vector_stores)) that makes it behave exactly like everything else in module 03 — you `.invoke(query)` it just like you'd invoke a model or a prompt, and it snaps into a `|` chain the same way.

- **Turning a vector store into a retriever.** `vector_store.as_retriever()` is the easiest way to get one — under the hood it's still doing the same similarity search from module 12, just wrapped so it fits into chains.
- **Tuning how it searches.** You can control how many results come back, whether it avoids near-duplicates, and whether it filters out weak matches entirely.
- **A ready-made "search then answer" combo.** `create_retrieval_chain` is a shortcut that does the whole thing for you: search for relevant documents, hand them to the model along with the question, and return both the model's answer and which documents it used.
- **Fancier retrievers wrap simpler ones.** Some retrievers add extra smarts on top of a basic one — for example, rephrasing a vague question into several different search queries to catch more relevant results. They all still work with the same `.invoke(query)` pattern, so you can swap a fancier one in without changing anything else.

## Use Case

This is the "R" in RAG: any time an LLM needs facts beyond its training data or system prompt (your internal docs, a knowledge base, current data), you retrieve relevant context first, then generate. Retrieval is also useful standalone — e.g. "show me the 3 most relevant support articles" without ever calling an LLM.

## How to Run

```bash
python modules/14_retrieval/example.py
python modules/14_retrieval/solutions.py   # exercise solutions
```
Requires an embeddings key and `ANTHROPIC_API_KEY`. `raw_retriever_demo()` only embeds and searches (no LLM call); `retrieval_chain_demo()` additionally calls Claude to generate the final `answer`.

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

**Solutions:** see [`solutions.py`](solutions.py) in this folder.

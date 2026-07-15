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

`build_retriever()` accepts a `search_type` argument (`"similarity"` or `"mmr"`) so you can experiment with both — see exercise 3 for putting that to use.

## Classes & Methods Used

| API | What It Does | Why We Use It Here |
|---|---|---|
| `store.as_retriever(search_type=..., search_kwargs={"k": 2})` | Wraps a vector store as a `Runnable` retriever, so it can be `.invoke()`-d or piped like anything else from module 03. | Used to turn the Chroma store from module 12 into something `create_retrieval_chain` (and chains in general) can accept directly. |
| `retriever.invoke(query)` | Runs the retriever's search and returns the matching `Document`s. | Used in `raw_retriever_demo()` to show the retriever working on its own, before it's wired into a full chain. |
| `create_stuff_documents_chain(llm, prompt)` | Builds a chain that takes retrieved documents, "stuffs" their text into the prompt's `{context}` slot, and calls the model. | Used as the "answer generation" half of the retrieval chain — it's what actually turns retrieved documents into a written answer. |
| `create_retrieval_chain(retriever, combine_docs_chain)` | Wires a retriever and a document-combining chain together: retrieve, then generate, returning both. | Used to build the complete "search then answer" pipeline in one call, instead of manually retrieving and then separately calling the combine-docs chain. |
| `result["answer"]` / `result["context"]` | The two keys `create_retrieval_chain`'s output dict always contains — the generated answer, and the documents that were used to produce it. | Used to print both the answer and its supporting evidence, so you can verify the answer is actually grounded in what was retrieved. |

## Using a different model

The retriever itself only depends on the embedding provider (via the underlying vector store); the "combine documents" / generation half of `create_retrieval_chain` uses whatever `get_chat_model(...)` you pass it.

## Reference Docs

- Retrieval concept: https://python.langchain.com/docs/concepts/retrievers/
- `create_retrieval_chain`: https://python.langchain.com/docs/how_to/qa_chat_history_how_to/
- `MultiQueryRetriever`: https://python.langchain.com/docs/how_to/MultiQueryRetriever/

## Exercises

1. **More retrieved context isn't automatically better.** In `retrieval_chain_demo()`, change `build_retriever()`'s `k` from 2 to 4 (so more documents get retrieved per query). Run the same question through and compare the answer to the `k=2` version — does having more context in the prompt help, or does it start pulling in less-relevant documents that dilute the answer?
2. **Rejecting a query with no good matches, instead of forcing k results.** Build a retriever with `search_type="similarity_score_threshold"` and `search_kwargs={"k": 4, "score_threshold": 0.6}` (module 12's exercise 3 covers the same idea at the vector-store level; this applies it at the retriever level). Ask a question totally unrelated to this module's 4-document corpus and confirm you get 0 results back, not 4 weak ones.
3. **Widening recall by rephrasing the query automatically.** `MultiQueryRetriever.from_llm(retriever=base_retriever, llm=llm)` wraps your base retriever with an LLM step that generates several differently-worded versions of the query before searching. Try it on a deliberately vague question (e.g. "how does LangChain find stuff") and compare its results to the plain base retriever's — does rephrasing surface documents the literal query missed?
4. **Verifying the answer is actually grounded in what was retrieved, not the model's general knowledge.** Run `create_retrieval_chain`'s result and print both `result["answer"]` and `result["context"]` (the list of documents that were actually retrieved). Read through the context and check: does every claim in the answer trace back to something in the context? This is the core trust-check for any RAG system.

**Solutions:** see [`solutions.py`](solutions.py) in this folder.

# 16 — RAG (Retrieval-Augmented Generation)

## Theory

RAG grounds an LLM's answer in retrieved evidence instead of relying purely on what it memorized during training. The canonical pipeline:

1. **Load** — pull in raw source documents (files, web pages, database rows).
2. **Split** — break long documents into chunks small enough to embed meaningfully and fit in a prompt (`RecursiveCharacterTextSplitter` is the standard default: splits on paragraph/sentence boundaries first, falling back to smaller separators).
3. **Embed & store** — embed each chunk and put it in a vector store ([modules 09-12](../09_embeddings_theory)).
4. **Retrieve** — given a user question, fetch the top-k most relevant chunks ([module 14](../14_retrieval)).
5. **Generate** — stuff the retrieved chunks into a prompt as context and ask the LLM to answer *using only that context*, ideally citing which chunk each claim came from.

RAG exists because of two hard limits on any LLM: a **fixed knowledge cutoff** (it doesn't know about your private data or anything after training) and a **finite context window** (you can't just paste your entire knowledge base into every prompt). Retrieval solves both by fetching only the handful of chunks relevant to *this* question.

## Use Case

Answering questions over an internal knowledge base, a product's documentation, a company's policies, or any corpus too large/private to bake into the model itself — while reducing hallucination by forcing the model to ground answers in retrieved text.

## How to Run

```bash
python modules/16_rag/example.py
python modules/16_rag/solutions.py   # exercise solutions
```
Requires an embeddings key and `ANTHROPIC_API_KEY`. The FAISS index is rebuilt in memory from `sample_data/handbook.txt` on every run (nothing persisted to disk); the second question is intentionally unanswerable from the handbook, to confirm the model says so instead of guessing.

## Walkthrough

`example.py`:
1. Loads a sample "company handbook" text (`sample_data/handbook.txt`).
2. Splits it with `RecursiveCharacterTextSplitter` (chunk_size=400, overlap=50).
3. Embeds chunks into a fresh FAISS index (in-memory, no local persistence needed for this demo).
4. Builds a RAG chain: `{"context": retriever | format_docs, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()`. For what that dict literal and `RunnablePassthrough()` actually do at runtime, see [module 03's Execution Internals](../03_chains_lcel#execution-internals-the-runnable-protocol).
5. Asks 2 questions, one answerable from the handbook and one that isn't, to demonstrate the model correctly saying "I don't know" for the latter.

## Using a different model

Swap the embedding provider (`common.embedding_factory`) and/or the generation model (`common.model_factory`) independently — RAG's retrieval and generation stages are decoupled by design.

## Reference Docs

- LangChain RAG tutorial: https://python.langchain.com/docs/tutorials/rag/
- `RecursiveCharacterTextSplitter`: https://python.langchain.com/docs/how_to/recursive_text_splitter/
- Anthropic's own RAG guidance: https://docs.anthropic.com/en/docs/build-with-claude/embeddings#how-to-get-started-with-voyage-ai

## Exercises

1. Change `chunk_size` from 400 to 150 and observe whether answer quality or citation granularity changes.
2. Add a question that's only answerable by combining facts from two different chunks, and check whether `k=2` retrieval is enough or if you need `k=4`.
3. Modify the prompt so the model must respond with `"NOT_FOUND"` (not prose) when the context doesn't contain the answer, and test it programmatically.
4. Swap `RecursiveCharacterTextSplitter` for `CharacterTextSplitter` (naive splitting) and compare chunk boundaries on the same document.

**Solutions:** see [`solutions.py`](solutions.py) in this folder.

# 16 — RAG (Retrieval-Augmented Generation)

## Theory

RAG (Retrieval-Augmented Generation) is a fancy name for a simple idea: instead of hoping the model already knows the answer, first go find the relevant facts, hand them to the model, and then ask it to answer using those facts. Here's the whole pipeline in plain steps:

1. **Load** — bring in your source material (documents, web pages, whatever you want the model to be able to answer questions about).
2. **Split** — cut long documents into smaller chunks. This matters for two reasons: a giant document doesn't embed well as one single "meaning" (module 09), and you can only fit so much text into one prompt anyway.
3. **Turn each chunk into an embedding and store it** — same idea as modules 09-12, just applied to your own documents.
4. **When a question comes in, find the most relevant chunks** — this is retrieval, from module 14.
5. **Hand those chunks to the model along with the question**, and tell it to answer *using only what you gave it* — ideally also saying which chunk it got each fact from, so you can double-check.

Why bother with all this instead of just asking the model directly? Two reasons: the model was only trained on data up to a certain point in time, so it simply doesn't know about your private documents or anything recent — and even if it did, you can't paste an entire company's worth of documents into a single prompt, there's a limit to how much text fits in one request. RAG solves both problems by fetching only the small handful of chunks that are actually relevant to *this* question.

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

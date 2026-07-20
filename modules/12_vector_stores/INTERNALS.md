# Module 12 — Internals

## `Document`

**What it is:** A simple data class — page content plus a metadata dict — used everywhere in LangChain to represent "one retrievable chunk of information," whether it came from a vector store, a file loader, or anywhere else.

**How it works internally:** Like `BaseMessage` (module 01), it's a thin Pydantic model. `Document(page_content="...", metadata={"category": "billing"})` just validates and stores those two fields — no logic. What matters is that it's the **universal currency** retrievers and vector stores pass around: every vector store's `.similarity_search()` returns a `list[Document]`, no matter which backend (Chroma, FAISS, or anything else) actually did the searching.

**Real source:** [`langchain_core/documents/base.py`](https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/documents/base.py).

## `Chroma`

**What it is:** A LangChain wrapper around the `chromadb` Python package — an embedded vector database that runs inside your own process (no separate server to start, unlike a database like PostgreSQL).

**How it works internally:**
1. `Chroma.from_documents(docs, embedding=embeddings_model)` first calls `embeddings_model.embed_documents([d.page_content for d in docs])` to turn every document into a vector (the exact same `Embeddings` interface from module 09), then hands those vectors — plus each document's text and metadata — to `chromadb` to actually store.
2. Internally, `chromadb` builds an index over the vectors (by default, an approximate-nearest-neighbor structure) so that future searches don't need to compare against every stored vector one by one — this is the same performance idea module 11's INTERNALS.md contrasts brute-force search against.
3. `.similarity_search(query, k=2)` embeds your query with the *same* embedding model the store was built with (this is why mismatched embedding providers cause nonsense results — module 15's Theory covers this for FAISS, and it applies equally here), searches the index, and returns the top `k` matches wrapped back up as `Document` objects.
4. `.similarity_search(..., filter={"category": "billing"})` adds a metadata pre-filter — `chromadb` narrows the candidate set to only documents whose metadata matches *before* (or alongside) the vector search, rather than searching everything and filtering afterward in Python.

**Real source:** The LangChain integration is in [`langchain_chroma`](https://github.com/langchain-ai/langchain/tree/master/libs/partners/chroma); the actual vector database logic is in the separate [`chroma-core/chroma`](https://github.com/chroma-core/chroma) repo.

**How to validate it's working:**
```python
store = build_store()
results = store.similarity_search("How do I get my money back?", k=2)
print(type(results[0]))          # <class 'langchain_core.documents.base.Document'>
print(results[0].metadata)       # {'category': 'billing'} -- confirms metadata survived the round-trip

# Confirm the filter genuinely restricts the search space, not just re-ranks:
billing_only = store.similarity_search("refund", k=10, filter={"category": "billing"})
print(all(doc.metadata["category"] == "billing" for doc in billing_only))  # True
```

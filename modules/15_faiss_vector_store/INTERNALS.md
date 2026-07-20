# Module 15 — Internals

## `FAISS` (the LangChain wrapper)

**What it is:** A LangChain `VectorStore` implementation built on top of Meta AI's `faiss` library — unlike `Chroma` (module 12), which wraps a full embedded database, FAISS itself is *just* an in-memory similarity-search index; LangChain's `FAISS` class adds the document storage, metadata, and persistence on top of it.

**How it works internally:**
1. `FAISS.from_documents(docs, embedding=...)` embeds every document (same `Embeddings` interface as everywhere else in this repo) and hands the resulting vectors to the underlying `faiss` library, which builds an index — by default, `IndexFlatL2`, which does *exact* nearest-neighbor search by literally comparing your query against every stored vector (this is the same brute-force idea from module 11, just implemented in fast, compiled C++ instead of a Python loop).
2. Alongside the FAISS index itself, the LangChain wrapper keeps a separate Python dict mapping each vector's position in the index back to its original `Document` (text + metadata) — this is necessary because the raw FAISS index only knows about numbers, not your original text.
3. `.similarity_search(query, k=2)` embeds the query, asks the FAISS index for the `k` nearest vectors (a fast, optimized operation — this is FAISS's whole reason to exist), then uses the position-to-document mapping to translate the index's numeric results back into real `Document` objects.

**Real source:** LangChain's wrapper is [`langchain_community/vectorstores/faiss.py`](https://github.com/langchain-ai/langchain/blob/master/libs/community/langchain_community/vectorstores/faiss.py); the actual index/search algorithms are in Meta's [`facebookresearch/faiss`](https://github.com/facebookresearch/faiss) repo (mostly C++, with Python bindings).

## `.save_local()` / `.load_local()`

**How it works internally:** `.save_local(folder)` writes two files: `index.faiss` (the raw FAISS index data, in FAISS's own binary format) and `index.pkl` (a Python pickle file containing the document mapping and embedding configuration described above). `.load_local(folder, embeddings, allow_dangerous_deserialization=True)` reads both files back — `index.faiss` gets loaded by the `faiss` library directly, and `index.pkl` gets unpickled by Python's standard `pickle` module. The `allow_dangerous_deserialization` flag exists specifically because `pickle.load()` can execute arbitrary code if the file was crafted maliciously — LangChain makes you opt in explicitly rather than silently trusting any file you point it at.

**How to validate persistence is really working (not just appearing to):**
```python
# After build_and_save():
import os
print(os.listdir(INDEX_DIR))   # ['index.faiss', 'index.pkl']
print(os.path.getsize(INDEX_DIR / "index.faiss"), "bytes")  # should be nonzero

# Confirm the reloaded store didn't need network/API calls to work:
# (temporarily break your API key, or just trust that .load_local() alone,
#  with no embed_documents() call happening, proves this by construction --
#  reading the code path confirms no Embeddings method is called during load)
reloaded_store = load_from_disk()
results = reloaded_store.similarity_search("How does FAISS persist data?", k=1)
print(results[0].page_content)   # should work instantly, no embedding computation needed for the stored docs
```

## `.add_documents()`

**How it works internally:** Embeds the new document(s) (one more call to the `Embeddings` interface), then calls the underlying FAISS index's own "add vectors" operation to insert them into the existing index structure, and adds corresponding entries to the document mapping. For `IndexFlatL2` specifically, this is cheap — there's no complex index structure to rebuild, just an append to the list of stored vectors.

**How to validate an update actually took effect:**
```python
before_count = len(reloaded_store.index_to_docstore_id)  # internal count of stored vectors
reloaded_store.add_documents([Document(page_content="A new fact about FAISS.")])
after_count = len(reloaded_store.index_to_docstore_id)
print(after_count - before_count)   # should be exactly 1
```

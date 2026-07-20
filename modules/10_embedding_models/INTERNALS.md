# Module 10 — Internals

Module 09's INTERNALS.md covers the shared `Embeddings` interface all three of these implement. This page covers what's actually different underneath each one.

## `VoyageAIEmbeddings`

**How it works internally:** Wraps the `voyageai` Python package (a thin HTTP client, the same relationship `langchain_anthropic` has with the `anthropic` package — module 01). `.embed_documents()` batches your texts into one or more HTTP requests to Voyage's API (there's a per-request size limit, so very large lists get automatically split into multiple requests internally), sends your `VOYAGE_API_KEY` in the request, and parses the returned vectors back out of the JSON response.

**Real source:** [`langchain_voyageai`](https://github.com/langchain-ai/langchain/tree/master/libs/partners/voyageai) in the `langchain-ai/langchain` repo.

## `OpenAIEmbeddings`

**How it works internally:** Same shape as `VoyageAIEmbeddings` — wraps the `openai` Python package, sends `OPENAI_API_KEY`, batches requests to OpenAI's embeddings endpoint. The main practical difference from Voyage is the model name and the vector dimensionality it returns (module 10's exercise 1 has you check this directly).

**Real source:** [`langchain_openai`](https://github.com/langchain-ai/langchain/tree/master/libs/partners/openai) — look in the `embeddings` submodule.

## `HuggingFaceEmbeddings`

**How it works internally:** This one is fundamentally different from the other two — there's no network call at all. It wraps the `sentence-transformers` Python package, which downloads a small neural network model file (once, cached locally after the first run) and runs it directly on your CPU (or GPU, if available) inside your own Python process. This is why it needs no API key: the "provider" is your own machine.

**Real source:** [`langchain_community/embeddings/huggingface.py`](https://github.com/langchain-ai/langchain/blob/master/libs/community/langchain_community/embeddings/huggingface.py); the actual model-running logic underneath comes from [`UKPLab/sentence-transformers`](https://github.com/UKPLab/sentence-transformers).

## How to validate all three, and see the difference directly

```python
for provider in ("voyage", "openai", "huggingface"):
    embeddings_model = get_embeddings(provider=provider)
    print(provider, type(embeddings_model).__module__)
    # voyage      -> langchain_voyageai.embeddings
    # openai      -> langchain_openai.embeddings.base
    # huggingface -> langchain_community.embeddings.huggingface
```
The `.__module__` on each object tells you exactly which package's code is actually running — useful whenever you're not sure which implementation `get_embeddings()` handed you.

To directly observe the "network call vs. local model" difference: temporarily disconnect your network (or just watch your OS's network activity monitor) while calling `.embed_documents()` on the HuggingFace provider — it should keep working, since it never leaves your machine, unlike Voyage/OpenAI which will fail or hang without a connection.

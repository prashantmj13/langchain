# Module 16 — Internals

The `{"context": ..., "question": ...} | prompt | llm | StrOutputParser()` chain shape is the same `RunnableParallel`/`RunnablePassthrough` pattern covered in [module 05's INTERNALS.md](../05_sequential_chain/INTERNALS.md), and `FAISS`/`as_retriever()` are covered in [module 15's](../15_faiss_vector_store/INTERNALS.md) and [module 14's](../14_retrieval/INTERNALS.md). What's new in this module is the text splitter.

## `RecursiveCharacterTextSplitter`

**What it is:** A `Runnable`-adjacent utility (technically a `TextSplitter`, a slightly different base class from `Runnable`, but used the same "build once, call `.split_text()` many times" way) that breaks a long string into smaller chunks, trying to respect natural text boundaries rather than cutting blindly every N characters.

**How it works internally:**
1. It's configured with a list of separators to try, in priority order — by default: `["\n\n", "\n", " ", ""]` (paragraph breaks, then line breaks, then spaces, then finally individual characters as a last resort).
2. `.split_text(text)` first tries splitting the whole text on the *first* separator (`"\n\n"`, paragraph breaks). If any resulting piece is still longer than `chunk_size`, it recursively re-splits *that piece* using the *next* separator in the list (`"\n"`), and so on — this is the "recursive" in the class name.
3. Once every piece is at or under `chunk_size`, it assembles the final chunks — but if `chunk_overlap > 0`, adjacent chunks are given some shared trailing/leading text, so a sentence that happens to fall right at a chunk boundary still appears in full in at least one chunk, instead of being cut in half with no chunk containing the complete thought.
4. This "try to break at natural boundaries first" strategy is exactly why it usually produces more coherent chunks than `CharacterTextSplitter` (module 16's exercise 4 compares them directly) — the naive splitter only ever tries one fixed separator, with no fallback logic.

**Real source:** [`langchain_text_splitters/character.py`](https://github.com/langchain-ai/langchain/blob/master/libs/text-splitters/langchain_text_splitters/character.py) in the `langchain-ai/langchain` repo — look for `RecursiveCharacterTextSplitter`.

**How to validate it's working as intended:**
```python
splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
chunks = splitter.split_text(handbook_text)

print(len(chunks))                        # however many chunks it produced
print(max(len(c) for c in chunks))        # should be <= 400 (roughly -- overlap can push it slightly over)
print(chunks[0][-50:] in chunks[1])       # True-ish: the overlap region should appear in both chunks

# Confirm it's actually respecting paragraph boundaries where possible:
for chunk in chunks[:2]:
    print(repr(chunk[:80]), "...")  # eyeball whether chunks start/end at sensible points, not mid-word
```

# Module 13 — Internals

`FAISS` and `Document` are covered in depth in [module 12's](../12_vector_stores/INTERNALS.md) and [module 15's](../15_faiss_vector_store/INTERNALS.md) INTERNALS.md pages (this module uses the same `FAISS.from_documents()`/`.similarity_search_with_score()` calls). What's specific to this module is using an entire multi-paragraph document — a resume — as the search *query*, rather than a short question.

## Using a whole document as a query, not a short phrase

**How it works internally:** `store.similarity_search_with_score(resume_text, k=3)` embeds `resume_text` — the *entire* resume, potentially several paragraphs — through the exact same `embed_query()` path a short question would go through (module 09's INTERNALS.md). There's nothing structurally different happening; a longer piece of text just produces one embedding vector that reflects the "average meaning" of everything in it, the same way a short query does. This works reasonably well here because the resume and the job postings share a lot of the same vocabulary and concepts (skills, technologies) — the embedding model picks up on that overlap regardless of length.

**Something worth noticing (and a real limitation):** because the whole resume gets compressed into one vector, very specific details can get diluted by everything else in the document — this is part of why [project 11 (PDF Knowledge Base Assistant)](../../projects/11_pdf_knowledge_base_assistant) and [module 16 (RAG)](../16_rag) split long documents into smaller chunks instead of embedding them whole: a chunk's vector represents one focused idea, not an average across a whole document.

**How to validate the matching is picking up on real signal, not noise:**
```python
store = build_job_store()
matches = store.similarity_search_with_score(resume_text, k=3)
for doc, score in matches:
    print(f"{score:.3f}  {doc.metadata['source']}")

# Sanity check: replace the resume with something obviously irrelevant and confirm scores drop
irrelevant_text = "I enjoy hiking, painting, and playing the guitar on weekends."
control_matches = store.similarity_search_with_score(irrelevant_text, k=3)
print("Real resume top score:", matches[0][1])
print("Irrelevant text top score:", control_matches[0][1])
# The real resume's top score should be meaningfully higher (more similar) than the irrelevant text's
```

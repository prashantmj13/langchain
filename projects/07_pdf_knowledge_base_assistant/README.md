# Project 07 — PDF Knowledge Base Assistant

**Domain:** PDF processing
**Difficulty:** Intermediate
**Time estimate:** 5-8 hours

## The Problem

You have a stack of PDFs — a product manual, some research papers, a set of internal policy documents, whatever you actually have lying around — and answering a question about them means manually searching through each one. You're going to build a chat assistant that can answer questions across a whole folder of your own PDFs, with follow-up questions working naturally, and citations back to which document (and ideally which page) an answer came from.

This is the RAG pattern from modules 16-17, applied to real PDFs instead of the repo's sample handbook text.

## What You'll Build

A command-line chat loop that:
1. On first run, loads every PDF in a folder you point it at, extracts the text, splits it into chunks, embeds them, and builds a vector store — saved to disk so you don't have to redo this every time.
2. On later runs, loads the existing vector store instead of rebuilding it (unless you've added new PDFs).
3. Lets you ask questions in a loop, with conversation history carried across turns (so "what about the second one?" works after you've asked about "the two main approaches").
4. Every answer cites which source document (and, if you can get it, page number) it came from — and says "I don't have that in these documents" when the answer genuinely isn't in your PDF set, instead of making something up.

## Suggested Approach

1. Gather 3-5 real PDFs you actually want to ask questions about — this project is far more motivating (and a better test of whether it actually works) with real documents than with throwaway samples.
2. Extract text from each PDF using `pypdf` (already in this repo's `requirements.txt`). Note that PDF text extraction is often messy — headers/footers repeating on every page, weird line breaks, tables turning into scrambled text. Look at what your extracted text actually looks like before assuming it's clean.
3. When you split the extracted text into chunks (module 16's `RecursiveCharacterTextSplitter` pattern), attach metadata to each chunk: which source file it came from, and ideally which page (you can extract text page-by-page with `pypdf` and tag each chunk with its page number as you go, rather than extracting the whole document as one blob).
4. Build the vector store with FAISS (module 15) and persist it to disk, so subsequent runs load instantly instead of re-embedding everything.
5. Layer in conversational RAG per module 17 — the history-aware retriever pattern, so follow-up questions get correctly rewritten before searching.
6. In your answer-generation prompt, explicitly require the model to cite `[source: filename, page: N]` for each claim, using the metadata you attached to each chunk — and to say it doesn't know when nothing relevant was retrieved.

## Tech You'll Need

- `pypdf` for text extraction
- `RecursiveCharacterTextSplitter`
- FAISS (`langchain_community.vectorstores.FAISS`) with local persistence
- `RunnableWithMessageHistory` for the conversation loop

## Stretch Goals

- Detect when a PDF has already been indexed (e.g. by hashing its contents) and skip re-processing it on subsequent runs, only processing newly-added files.
- Handle PDFs with tables reasonably — either accept the messiness, or look into a PDF library that extracts tables more cleanly, and compare the difference in answer quality.
- Add a `/sources` command that, given the last answer, prints the full text of the chunks that were actually retrieved and used — useful for building trust in (or catching mistakes in) the answers.
- Try chunk sizes and `k` (retrieved chunk count) different from the repo's defaults and see how answer quality changes on your specific documents — different document types (dense academic papers vs. simple manuals) likely want different settings.

## Definition of Done

You can ask at least 5 real questions about your PDF set and get answers that are actually grounded in the documents (verify by checking the cited source/page yourself), including at least one multi-turn follow-up question that correctly uses the earlier conversation's context, and at least one question that's genuinely not answerable from your documents — which the assistant should say so, rather than inventing an answer.

## Reference Modules

- [15 — FAISS Vector Store](../../modules/15_faiss_vector_store)
- [16 — RAG](../../modules/16_rag)
- [17 — History-Aware RAG Bot](../../modules/17_history_aware_rag_bot)

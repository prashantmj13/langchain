# 17 — History-Aware RAG Bot

## Theory

Plain RAG ([module 16](../16_rag)) breaks in an ordinary conversation. Say a user asks "How much PTO do I get?" and then follows up with "How much of that carries over?" — if you search your documents using the literal words "how much of that carries over," the word "that" refers to nothing on its own, and the search comes back useless. Humans understand "that" from context; a plain retriever doesn't.

The fix: before searching, first ask the model to *rewrite* the follow-up question into a standalone one — turning "how much of that carries over?" into "how much unused PTO carries over to the next year?" using the earlier conversation as context. *Then* search using that rewritten question, and finally answer using both what was found and the original conversation. LangChain gives you ready-made pieces for each part of this:

- **A step that rewrites the question first.** This is a small model call that happens before the actual search, using chat history to turn a vague follow-up into a clear, standalone question.
- **The same "search then answer" combo from module 14**, just with the rewriting step bolted on in front of it.
- **The same conversation-memory wrapper from [module 07](../07_chat_history)**, so history is loaded and saved automatically without you managing it by hand.

## Use Case

Any conversational assistant over a knowledge base — a docs chatbot, an internal support bot — where users naturally ask follow-up questions ("what about X", "and if Y instead") that only make sense in light of the prior turn.

## How to Run

```bash
python modules/17_history_aware_rag_bot/example.py
python modules/17_history_aware_rag_bot/solutions.py   # exercise solutions
```
Requires an embeddings key and `ANTHROPIC_API_KEY`. Conversation history lives in the same in-memory `_store` pattern as module 07 — it resets each time you re-run the script. Watch the 2nd and 3rd questions: neither repeats "PTO" or "remote work" by name, yet both get answered correctly because the history-aware retriever rewrites them first.

## Walkthrough

`example.py` reuses the handbook corpus from module 16:
1. Builds a history-aware retriever (Claude rewrites the question using chat history, then searches FAISS).
2. Builds the full retrieval chain (history-aware retriever + answer generation).
3. Wraps it in `RunnableWithMessageHistory`.
4. Runs a 3-turn conversation: "How much PTO do full-time employees get?" → "How much of that carries over?" → "And what about remote work days per week?" — each follow-up only works because history reshapes the retrieval query.

## Classes & Methods Used

| API | What It Does | Why We Use It Here |
|---|---|---|
| `create_history_aware_retriever(llm, retriever, contextualize_prompt)` | Wraps a plain retriever with an LLM step that first rewrites the incoming question using chat history, *then* searches. | This is the one new piece versus module 16 — it's what makes "how much of that carries over?" resolve correctly instead of searching for the literal word "that". |
| `create_stuff_documents_chain(llm, answer_prompt)` | Builds the "take retrieved documents, put them in the prompt, generate an answer" step (same as module 14). | Used as the second half of the pipeline — answering, once the history-aware retriever has found the right chunks. |
| `create_retrieval_chain(history_aware_retriever, combine_docs_chain)` | Wires the retriever and answer-generation step together into one pipeline (same helper as module 14, just given a history-aware retriever instead of a plain one). | Produces the complete "rewrite → search → answer" chain in one object. |
| `MessagesPlaceholder("chat_history")` | A spot in a prompt template that gets filled with the running list of prior messages (same as module 07). | Used in *two* prompts here — the rewriting prompt needs history to know what "that" refers to, and the answering prompt needs it too, for natural-sounding replies. |
| `RunnableWithMessageHistory(rag_chain, get_session_history, ..., output_messages_key="answer")` | Wraps the whole RAG chain so history loads/saves automatically per session (same as module 07). | `output_messages_key="answer"` tells it which key in the chain's output dict is the actual reply to save into history — needed here because `create_retrieval_chain` returns a dict (`answer` + `context`), not a single message like module 07's plain chain did. |

For how `create_history_aware_retriever` actually decides whether/how to rewrite a question before searching — plus a way to prove the rewriting is genuinely improving retrieval, not just adding latency — see [`INTERNALS.md`](INTERNALS.md) in this folder.

## Using a different model

Both the query-rewriting step and the final-answer step accept any `get_chat_model(...)`; they can even use two different models (e.g. a fast/cheap model to rewrite, Claude to generate the final answer) since they're separate `Runnable`s under the hood.

## Reference Docs

- Conversational RAG tutorial: https://python.langchain.com/docs/tutorials/qa_chat_history/
- `create_history_aware_retriever`: https://python.langchain.com/api_reference/langchain/chains/langchain.chains.history_aware_retriever.create_history_aware_retriever.html

## Exercises

1. **Seeing the rewritten question, not just the final answer.** `create_history_aware_retriever` rewrites your follow-up internally before searching — `example.py` never shows you that intermediate step. Build the `contextualize_prompt | llm` chain separately, call `.invoke({"chat_history": ..., "input": "How much of that carries over?"})` on it directly, and print the result — you should see something like "How much unused PTO carries over to the next year?" instead of the original vague question.
2. **A follow-up that needs 2 earlier turns combined, not 1.** After asking about PTO and then remote work (like `example.py` does), ask a third question like "Compare those two policies — which is more generous?" This requires the rewriting step to correctly pull context from *two* prior turns, not just the most recent one — check whether it does.
3. **Using a cheaper model for the "boring" rewriting step.** The query-rewriting step doesn't need Claude's full reasoning power — it's a mechanical rewrite, not deep reasoning. Build `create_history_aware_retriever` with a cheaper/faster model (e.g. `get_chat_model(provider="openai", model="gpt-4o-mini")`) while keeping Claude for the final answer-generation step. Time both versions and confirm answer quality doesn't noticeably drop.
4. **Comparing the retriever-chain approach to the agent approach.** Instead of `create_history_aware_retriever`, build a [module 19](../19_agents)-style agent with `create_react_agent`, giving it the plain (non-history-aware) retriever wrapped as a `@tool`. Ask it the same 3-turn conversation from `example.py` and compare: does the agent naturally figure out to rephrase its own search queries based on context, without you needing a separate rewriting step?

**Solutions:** see [`solutions.py`](solutions.py) in this folder.

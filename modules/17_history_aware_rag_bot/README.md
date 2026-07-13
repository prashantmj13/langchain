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

## Using a different model

Both the query-rewriting step and the final-answer step accept any `get_chat_model(...)`; they can even use two different models (e.g. a fast/cheap model to rewrite, Claude to generate the final answer) since they're separate `Runnable`s under the hood.

## Reference Docs

- Conversational RAG tutorial: https://python.langchain.com/docs/tutorials/qa_chat_history/
- `create_history_aware_retriever`: https://python.langchain.com/api_reference/langchain/chains/langchain.chains.history_aware_retriever.create_history_aware_retriever.html

## Exercises

1. Print the *rewritten* standalone question for each follow-up turn (not just the final answer) to see exactly what the retriever searched with.
2. Ask a follow-up that requires combining two earlier turns' context (e.g. "compare that to the remote work policy") and see whether it resolves correctly.
3. Swap the query-rewriting LLM to a cheaper/faster model than the answer-generation LLM and compare latency without losing correctness.
4. Rebuild this using LangGraph's `create_react_agent` with a retriever exposed as a tool instead of the `create_history_aware_retriever` helper, and compare the two approaches.

**Solutions:** see [`solutions.py`](solutions.py) in this folder.

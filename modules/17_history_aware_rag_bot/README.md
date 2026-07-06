# 17 — History-Aware RAG Bot

## Theory

Plain RAG ([module 16](../16_rag)) breaks down in a multi-turn conversation. If a user asks "How much PTO do I get?" then follows up with "How much of that carries over?", a bare retriever embeds "How much of that carries over?" in isolation — "that" resolves to nothing, and retrieval fails.

The fix is **query reformulation**: before retrieving, use the LLM (with chat history) to rewrite the follow-up into a standalone question ("How much unused PTO carries over to the next year?"), *then* retrieve with the rewritten query, and finally generate the answer using both the retrieved context and the original conversation history. LangChain packages this as:

- **`create_history_aware_retriever`** — wraps a retriever with an LLM step that rewrites the incoming question using chat history before searching.
- **`create_retrieval_chain`** — combines the history-aware retriever with a "combine documents" answer-generation step (same helper as module 14, now history-aware upstream).
- **`RunnableWithMessageHistory`** ([module 07](../07_chat_history)) — wraps the whole thing so history is loaded/saved automatically per session.

## Use Case

Any conversational assistant over a knowledge base — a docs chatbot, an internal support bot — where users naturally ask follow-up questions ("what about X", "and if Y instead") that only make sense in light of the prior turn.

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

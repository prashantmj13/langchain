# Project 13 — FAQ Chatbot with Memory

**Domain:** Warm-up (general LangChain basics)
**Difficulty:** Beginner (the last of the warm-up projects — a little more involved than 09-12)
**Time estimate:** 2-3 hours

**Before you start:** Complete projects 09-12 first, and read [module 07 — Chat History](../../modules/07_chat_history) (just the theory and example, you don't need to have done its exercises). This project is where the warm-up track and the main `modules/` curriculum meet.

## The Problem

All four previous warm-up projects answered exactly one request and stopped. Real chat experiences remember what you said earlier in the conversation. You're going to build a small FAQ chatbot for a topic of your choice (a hobby, a game you play, a subject you know well) that can hold an actual back-and-forth conversation — including follow-up questions that only make sense in light of what was already said.

## What You'll Build

A command-line chat loop where:
1. You write a short system prompt describing what the bot knows about and how it should behave (e.g. "You are a helpful assistant that answers questions about houseplant care.").
2. The user can type questions one after another, in a loop, until they type `quit` or `exit`.
3. The bot remembers the whole conversation — a follow-up like "what about the second one?" or "how often, exactly?" correctly refers back to something mentioned earlier.

## Step-by-Step Guide

1. Create `faq_chatbot.py` with the usual bootstrap. This time you'll need a few more imports — go back to [module 07's `example.py`](../../modules/07_chat_history/example.py) and read through it carefully before starting; you're going to build something structurally very similar, on a topic of your own choosing.

2. **Pick your topic and write a system prompt for it.** Be specific — "You are a helpful assistant" is too vague; "You are a helpful assistant that answers questions about basic houseplant care: watering, light, and common problems. If asked about something outside houseplants, say so politely." is the kind of specificity that makes a small chatbot feel purposeful instead of generic.

3. **Set up message history storage**, following module 07's pattern exactly: a `ChatMessageHistory` object, and a `get_session_history()` function. Since this project only needs *one* ongoing conversation (not multiple users), you can simplify module 07's dict-of-sessions down to a single global history object if you prefer — but using the same `session_id` pattern as module 07 works fine too, and makes the stretch goal below easier.

4. **Build your prompt template** with a `MessagesPlaceholder` for history, exactly like module 07's example — this is the piece that lets prior turns actually reach the model.

5. **Wrap your chain in `RunnableWithMessageHistory`**, same as module 07.

6. **Write the chat loop.** This is the new structural piece for this project — a `while True:` loop that:
   - Prompts the user for input with `input("You: ")`.
   - Checks if they typed `quit` or `exit` (case-insensitive) and breaks out of the loop if so.
   - Otherwise, invokes your chain with their message and prints the response.
   ```python
   while True:
       user_input = input("You: ")
       if user_input.strip().lower() in ("quit", "exit"):
           print("Goodbye!")
           break
       response = chain_with_history.invoke(
           {"input": user_input}, config={"configurable": {"session_id": "chat"}}
       )
       print("Bot:", response.content)
   ```

7. Run it and have an actual multi-turn conversation — ask an initial question, then ask a follow-up that only makes sense given your first question (e.g. "What's the second one?" after the bot lists a few options), and confirm it correctly understands what you're referring to.

## Example to Test Against

With a houseplant-care system prompt, try this sequence:
1. "What are three easy houseplants for a beginner?"
2. "How often should I water the second one?" — this should correctly know which plant "the second one" refers to, without you naming it again.
3. "What if the leaves start turning yellow?" — should stay in context of whichever plant you were just discussing.

## Common Mistakes

- **Forgetting the `config={"configurable": {"session_id": "..."}}` argument** on `.invoke()` — without it, `RunnableWithMessageHistory` won't know which conversation's history to load/save, and you'll get an error or, depending on your setup, unexpected behavior.
- **Using the same `session_id` inconsistently** — if you accidentally use a different session ID string on different calls, each call will get a fresh, empty history instead of continuing the same conversation. Store it in a variable once at the top of your script rather than retyping the string.
- **The loop never ending** — double-check your exit condition actually matches what you type (`"quit"` vs `"Quit"` vs `"q"`) — `.strip().lower()` on the input before comparing avoids most of these mismatches.

## Stretch Goals

- Add a `/history` command that, when typed instead of a question, prints the full conversation so far (reuse ideas from [module 08 — Display History](../../modules/08_display_history)).
- Support multiple named conversations in one run — let the user type `/new <name>` to switch to a fresh session with a different `session_id`, and switch back with `/switch <name>`.
- Save the conversation to a file when the user exits, so it's not lost when the script ends (module 08's JSON export pattern is a good starting point).

## Definition of Done

You can have a real conversation of at least 5 exchanges where at least 2 of your questions are follow-ups that only make sense because the bot remembers earlier turns — and it answers them correctly, staying on-topic for your chosen subject.

## Reference Modules

- [07 — Chat History](../../modules/07_chat_history)
- [08 — Display History](../../modules/08_display_history) (for the stretch goals)
- [02 — Prompt Templates](../../modules/02_prompt_templates)

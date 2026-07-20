# Module 08 — Internals

This module doesn't introduce new LangChain classes — it's entirely built on `BaseMessage`/`HumanMessage`/`AIMessage` (covered in [module 01's INTERNALS.md](../01_langchain_basics/INTERNALS.md)) and `ChatMessageHistory` (covered in [module 07's INTERNALS.md](../07_chat_history/INTERNALS.md)). What's worth understanding here specifically is *why* `.type` and `.content` are reliable enough to build formatters around.

## `message.type` and `message.content` as a stable formatting contract

**What it is:** Every message class in LangChain — no matter which provider produced it, no matter whether it came from your code or a model's response — guarantees these two attributes exist and behave consistently. That stability is what lets one formatter (`print_transcript`, `to_markdown`, `to_json`) work on messages from *any* source.

**How it works internally:**
1. `.type` isn't computed at runtime — it's a fixed class-level attribute. `HumanMessage.type` is hardcoded to the literal string `"human"` in the class definition itself (similarly `"ai"` for `AIMessage`, `"system"` for `SystemMessage`). Every instance of that class shares the same `.type`, which is why you can reliably branch on it (`if message.type == "human"`) without worrying about it varying instance-to-instance.
2. `.content` is more flexible by design — for a plain-text message it's a `str`, but module 18 shows it can also be a `list` of content blocks (for multimodal messages). Any formatter that assumes `.content` is always a plain string (like this module's formatters do) will need adjusting once you introduce multimodal messages — worth keeping in mind if you extend this module's patterns elsewhere.
3. Because `BaseMessage` is a Pydantic model, all of this is enforced by Pydantic's validation at construction time — you can't accidentally create a `HumanMessage` with `.type = "ai"`, which is exactly the kind of guarantee that makes it safe to build formatting/display code around these fields without defensive checks.

**Real source:** [`langchain_core/messages/base.py`](https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/messages/base.py) defines `BaseMessage`; each subclass (`human.py`, `ai.py`, `system.py` in the same directory) sets its own fixed `.type`.

**How to validate this guarantee holds:**
```python
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

for msg in [HumanMessage(content="a"), AIMessage(content="b"), SystemMessage(content="c")]:
    print(msg.type, "->", type(msg.content))
# human -> <class 'str'>
# ai -> <class 'str'>
# system -> <class 'str'>
```
If you ever see `.content` come back as something other than a `str` in a script that assumes plain text (like this module's formatters), that's your signal you've received a multimodal message (module 18) and need to handle it differently.

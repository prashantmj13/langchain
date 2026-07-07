"""
Module 08 - Exercise solutions.

Run: python modules/08_display_history/solutions.py
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage

from common.model_factory import get_chat_model

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def _run_short_conversation() -> ChatMessageHistory:
    llm = get_chat_model()
    history = ChatMessageHistory()
    for user_input in ["What is a vector database?", "Give one popular example."]:
        history.add_user_message(user_input)
        history.add_ai_message(llm.invoke(history.messages).content)
    return history


def exercise_1():
    """Add a timestamp to each message as it's displayed (stored alongside, not on the message)."""
    llm = get_chat_model()
    history = ChatMessageHistory()
    timestamped = []

    for user_input in ["What is LangChain?"]:
        history.add_user_message(user_input)
        timestamped.append((datetime.now().isoformat(timespec="seconds"), history.messages[-1]))

        response = llm.invoke(history.messages)
        history.add_ai_message(response.content)
        timestamped.append((datetime.now().isoformat(timespec="seconds"), history.messages[-1]))

    print("--- Exercise 1: timestamped transcript ---")
    for ts, message in timestamped:
        print(f"[{ts}] [{message.type.upper()}] {message.content}")


def exercise_2():
    """Redact anything that looks like an email address before printing."""
    history = ChatMessageHistory()
    history.add_user_message("You can reach me at jane.doe@example.com if you need anything.")
    history.add_ai_message("Got it, I won't share that with anyone.")

    print("\n--- Exercise 2: redacted transcript ---")
    for message in history.messages:
        redacted = EMAIL_RE.sub("[redacted-email]", message.content)
        print(f"[{message.type.upper()}] {redacted}")


def exercise_3():
    """Render the transcript as HTML."""
    history = _run_short_conversation()

    lines = ['<div class="transcript">']
    for message in history.messages:
        css_class = "human" if message.type == "human" else "ai"
        lines.append(f'  <div class="{css_class}">{message.content}</div>')
    lines.append("</div>")
    html = "\n".join(lines)

    print("\n--- Exercise 3: HTML transcript ---")
    print(html)


def exercise_4():
    """Write the JSON transcript to a file and reload it into typed messages."""
    history = ChatMessageHistory()
    history.add_user_message("Hello!")
    history.add_ai_message("Hi there, how can I help?")

    payload = [{"role": m.type, "content": m.content} for m in history.messages]
    out_path = Path(__file__).resolve().parent / "transcript_demo.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    reloaded_payload = json.loads(out_path.read_text(encoding="utf-8"))
    role_to_cls = {"human": HumanMessage, "ai": AIMessage}
    reloaded_messages = [role_to_cls[item["role"]](content=item["content"]) for item in reloaded_payload]

    print("\n--- Exercise 4: write/reload JSON transcript ---")
    print(f"Wrote to {out_path}")
    print(f"Reloaded {len(reloaded_messages)} messages:", [m.content for m in reloaded_messages])


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()

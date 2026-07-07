"""
Module 18 - Exercise solutions.

Run: python modules/18_image_processing/solutions.py
"""

import base64
import io
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import HumanMessage
from PIL import Image, ImageDraw

from common.model_factory import get_chat_model


def _generate_image(text: str, color) -> str:
    image = Image.new("RGB", (400, 200), color=color)
    draw = ImageDraw.Draw(image)
    draw.rectangle([20, 20, 380, 180], outline=(255, 255, 255), width=3)
    draw.text((40, 90), text, fill=(255, 255, 255))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def _image_block(image_b64: str) -> dict:
    return {"type": "image", "source_type": "base64", "data": image_b64, "mime_type": "image/png"}


def exercise_1():
    """Swap the placeholder for a real photo on disk (falls back to a generated image if none provided)."""
    real_photo_path = Path(__file__).resolve().parent / "my_photo.jpg"
    llm = get_chat_model()

    if real_photo_path.exists():
        image_b64 = base64.b64encode(real_photo_path.read_bytes()).decode("utf-8")
        mime_type = "image/jpeg"
    else:
        print(f"(No {real_photo_path.name} found -- using a generated placeholder instead.)")
        image_b64 = _generate_image("Sample Photo", (70, 30, 90))
        mime_type = "image/png"

    message = HumanMessage(
        content=[
            {"type": "text", "text": "Describe what's in this image."},
            {"type": "image", "source_type": "base64", "data": image_b64, "mime_type": mime_type},
        ]
    )
    print("--- Exercise 1 ---")
    print(llm.invoke([message]).content)


def exercise_2():
    """Send two images in one message and ask Claude to compare them."""
    llm = get_chat_model()
    image_a = _generate_image("Option A", (30, 60, 114))
    image_b = _generate_image("Option B", (150, 40, 40))

    message = HumanMessage(
        content=[
            {"type": "text", "text": "Compare these two images. What's different between them?"},
            _image_block(image_a),
            _image_block(image_b),
        ]
    )
    print("\n--- Exercise 2: comparing two images ---")
    print(llm.invoke([message]).content)


def exercise_3():
    """Ask Claude to transcribe text drawn on the image, verify it's exact."""
    llm = get_chat_model()
    expected_text = "HELLO MCP"
    image_b64 = _generate_image(expected_text, (20, 90, 50))

    message = HumanMessage(
        content=[
            {"type": "text", "text": "Transcribe exactly the text you see in this image, nothing else."},
            _image_block(image_b64),
        ]
    )
    transcription = llm.invoke([message]).content.strip()

    print("\n--- Exercise 3: transcription accuracy ---")
    print(f"Expected:  {expected_text}")
    print(f"Got:       {transcription}")
    print(f"Exact match: {expected_text.lower() in transcription.lower()}")


def exercise_4():
    """Compare the same multimodal message against OpenAI's GPT-4o-mini."""
    image_b64 = _generate_image("LangChain + Claude", (30, 60, 114))
    message = HumanMessage(
        content=[
            {"type": "text", "text": "Describe this image."},
            _image_block(image_b64),
        ]
    )

    print("\n--- Exercise 4: Anthropic vs OpenAI on the same multimodal message ---")
    for provider, model in [("anthropic", None), ("openai", "gpt-4o-mini")]:
        try:
            llm = get_chat_model(provider=provider, model=model) if model else get_chat_model(provider=provider)
            print(f"\n[{provider}]")
            print(llm.invoke([message]).content)
        except Exception as exc:  # noqa: BLE001
            print(f"\n[{provider}] skipped ({exc.__class__.__name__}: {exc})")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()

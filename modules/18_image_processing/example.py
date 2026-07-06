"""
Module 18 - Image Processing: Claude's multimodal vision input.

Run: python modules/18_image_processing/example.py
"""

import base64
import io
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import HumanMessage
from PIL import Image, ImageDraw

from common.model_factory import get_chat_model


def generate_placeholder_image() -> str:
    """Draws a simple placeholder PNG and returns it as a base64 string."""
    image = Image.new("RGB", (400, 200), color=(30, 60, 114))
    draw = ImageDraw.Draw(image)
    draw.rectangle([20, 20, 380, 180], outline=(255, 255, 255), width=3)
    draw.text((60, 90), "LangChain + Claude", fill=(255, 255, 255))

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def describe_image(image_b64: str) -> str:
    llm = get_chat_model()
    message = HumanMessage(
        content=[
            {"type": "text", "text": "Describe this image, and read back any text you see in it."},
            {
                "type": "image",
                "source_type": "base64",
                "data": image_b64,
                "mime_type": "image/png",
            },
        ]
    )
    response = llm.invoke([message])
    return response.content


if __name__ == "__main__":
    image_b64 = generate_placeholder_image()
    print("--- Claude's description of the generated image ---")
    print(describe_image(image_b64))

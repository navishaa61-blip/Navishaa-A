from pathlib import Path
import re

from PIL import Image, ImageDraw, ImageFont
from huggingface_hub import InferenceClient

from app.config import settings

BASE_DIR = Path(__file__).resolve().parent.parent
PANEL_DIR = BASE_DIR / "static" / "panels"
PANEL_DIR.mkdir(parents=True, exist_ok=True)


def _safe_name(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9_-]+", "-", text).strip("-")
    return text[:80] or "panel"


def _demo_image(prompt: str, output_path: Path, panel_number: int) -> None:
    image = Image.new("RGB", (1024, 768), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((18, 18, 1006, 750), outline="black", width=8)
    draw.text((55, 55), f"COMICCRAFT • PANEL {panel_number}", fill="black")
    # Simple visual placeholder so the entire application is testable without paid AI.
    draw.ellipse((380, 170, 650, 440), outline="black", width=8)
    draw.arc((425, 245, 605, 390), 20, 160, fill="black", width=6)
    draw.text((55, 650), "DEMO IMAGE — configure HF_TOKEN for AI images.", fill="black")
    image.save(output_path)


def _huggingface_image(prompt: str, output_path: Path) -> None:
    if not settings.hf_token:
        raise RuntimeError("HF_TOKEN is not configured for image generation.")

    client = InferenceClient(
        provider=settings.image_provider,
        api_key=settings.hf_token,
    )
    image = client.text_to_image(
        prompt,
        model=settings.image_model,
    )
    image.save(output_path)


def generate_image(prompt: str, panel_number: int) -> str:
    filename = f"panel-{panel_number}-{_safe_name(prompt)}.png"
    output_path = PANEL_DIR / filename

    if settings.image_backend == "demo" or settings.demo_mode:
        _demo_image(prompt, output_path, panel_number)
    elif settings.image_backend == "huggingface":
        _huggingface_image(prompt, output_path)
    else:
        raise RuntimeError(
            "Unsupported IMAGE_BACKEND. Use 'huggingface' or 'demo'."
        )

    return str(output_path)

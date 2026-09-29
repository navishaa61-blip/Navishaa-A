import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "ComicCraft")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_flash_model: str = os.getenv("GEMINI_FLASH_MODEL", "gemini-2.5-flash")
    gemini_pro_model: str = os.getenv("GEMINI_PRO_MODEL", "gemini-2.5-pro")
    hf_token: str = os.getenv("HF_TOKEN", "")
    image_model: str = os.getenv(
        "IMAGE_MODEL", "black-forest-labs/FLUX.1-schnell"
    )
    export_dir: str = os.getenv("EXPORT_DIR", "static/exports")
    image_provider: str = os.getenv("IMAGE_PROVIDER", "auto")
    image_backend: str = os.getenv("IMAGE_BACKEND", "huggingface")
    demo_mode: bool = as_bool(os.getenv("DEMO_MODE"), False)
    panels: int = int(os.getenv("PANELS", "5"))
    max_prompt_chars: int = int(os.getenv("MAX_PROMPT_CHARS", "1200"))
    seed: int = int(os.getenv("IMAGE_SEED", "0"))


settings = Settings()

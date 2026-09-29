import json

from google import genai
from google.genai import types

from app.config import settings
from app.schemas import ComicOutline


def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> ComicOutline:

    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    prompt = f"""
Create a cohesive {settings.panels}-panel comic outline.

User story idea: {story_prompt}
Main character: {character_name}
Setting: {setting}
Tone: {tone}
Art style: {art_style}

Requirements:
- Exactly {settings.panels} panels.
- Keep the same main character and setting throughout.
- Each panel must advance the story.
- scene_description should describe visible action and environment.
- image_prompt must be a detailed prompt for an image-generation model.
- Do not put speech text inside image_prompt.
- Return only data matching the requested JSON schema.
""".strip()

    with genai.Client(
        api_key=settings.gemini_api_key
    ) as client:

        response = client.models.generate_content(
            model=settings.gemini_flash_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.9,
                response_mime_type="application/json",
                response_schema=ComicOutline,
            ),
        )

    raw = response.text

    if not raw:
        raise RuntimeError(
            "Gemini returned an empty outline."
        )

    try:
        return ComicOutline.model_validate_json(raw)

    except Exception:
        try:
            return ComicOutline.model_validate(
                json.loads(raw)
            )

        except Exception as exc:
            raise RuntimeError(
                f"Could not parse Gemini outline: {exc}"
            ) from exc
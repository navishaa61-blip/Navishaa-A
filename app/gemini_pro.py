import json

from google import genai
from google.genai import types

from app.config import settings
from app.schemas import ComicOutline, ComicStory


def generate_story(
    outline: ComicOutline,
    character_name: str,
    tone: str,
) -> ComicStory:

    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    outline_json = outline.model_dump_json(indent=2)

    prompt = f"""
Turn this comic outline into polished comic narration and dialogue.

Main character: {character_name}
Tone: {tone}

Outline:
{outline_json}

Requirements:
- Preserve the exact panel numbers and titles.
- Keep continuity between panels.
- Make each panel concise enough for a comic page.
- caption: short ambient/context text.
- narration: short narrator text.
- dialogue: natural dialogue; if nobody speaks, use an empty string.
- Return only data matching the requested JSON schema.
""".strip()

    with genai.Client(
        api_key=settings.gemini_api_key
    ) as client:

        response = client.models.generate_content(
          model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.85,
                response_mime_type="application/json",
                response_schema=ComicStory,
            ),
        )

    raw = response.text

    if not raw:
        raise RuntimeError(
            "Gemini returned an empty story."
        )

    try:
        return ComicStory.model_validate_json(raw)

    except Exception:
        try:
            return ComicStory.model_validate(
                json.loads(raw)
            )

        except Exception as exc:
            raise RuntimeError(
                f"Could not parse Gemini story: {exc}"
            ) from exc
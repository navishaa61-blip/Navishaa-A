# ComicCraft — AI Comic Story Creator

ComicCraft is a FastAPI web application based on the supplied project specification. It collects a story prompt, character name, setting, tone, and art style, then creates a 5-panel comic with narration, dialogue, illustrations, preview, and PDF export.

## Architecture

- Frontend: HTML + CSS + Jinja2
- Backend: FastAPI
- Story outline: Google Gemini structured JSON
- Story/dialogue: Google Gemini structured JSON
- Images: Hugging Face Inference Providers text-to-image
- Export: fpdf2
- Test/demo mode: local generated placeholder images and deterministic sample story

The original documentation names Gemini 1.5 Flash/Pro and `runwayml/stable-diffusion-v1-5`. Those model choices are now configurable because AI model availability changes over time. The code defaults to current configurable Gemini model names and a Hugging Face diffusion image model.

## Quick start — Windows

```powershell
cd ComicCraft
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Open:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/health

## First test without API keys

Keep `DEMO_MODE=true` in `.env`, start the server, fill in the form, and click Generate. This verifies the frontend, FastAPI routes, Jinja2 templates, image handling, layout building, and PDF export.

## Real AI generation

1. Put your Gemini API key in `GEMINI_API_KEY`.
2. Put a Hugging Face token with the required inference permission in `HF_TOKEN`.
3. Set `DEMO_MODE=false`.
4. Start the server again.

Example:

```env
GEMINI_API_KEY=your_key_here
HF_TOKEN=hf_your_token_here
DEMO_MODE=false
IMAGE_BACKEND=huggingface
IMAGE_PROVIDER=auto
IMAGE_MODEL=black-forest-labs/FLUX.1-schnell
```

## API test

Use FastAPI Swagger at `/docs`.

POST `/generate-comic/json` with:

```json
{
  "story_prompt": "A brave fox explores an enchanted forest.",
  "character_name": "Luna",
  "setting": "Enchanted forest",
  "tone": "adventurous",
  "art_style": "comic book"
}
```

## Image generation note

The supplied documentation proposes local Hugging Face Diffusers + Stable Diffusion. A local Diffusers installation is intentionally separated into `requirements-local-ai.txt` because PyTorch/model downloads can be very large and local generation is usually much slower without a suitable GPU.

The default implementation uses Hugging Face Inference Providers through `huggingface_hub`, so the app can run without downloading a diffusion model to the developer's computer.

## Project structure

```text
ComicCraft/
├─ app/
│  ├─ __init__.py
│  ├─ main.py
│  ├─ config.py
│  ├─ schemas.py
│  ├─ routes.py
│  ├─ gemini_flash.py
│  ├─ gemini_pro.py
│  ├─ image_generator.py
│  ├─ layout_builder.py
│  └─ exporters.py
├─ templates/
│  ├─ base.html
│  ├─ index.html
│  ├─ comic_preview.html
│  └─ export_success.html
├─ static/
│  ├─ css/style.css
│  ├─ panels/
│  └─ exports/
├─ requirements.txt
├─ requirements-local-ai.txt
├─ .env.example
├─ .gitignore
└─ README.md
```

## Troubleshooting

- `GEMINI_API_KEY is not configured`: either set the key or use `DEMO_MODE=true`.
- `HF_TOKEN is not configured`: either set the token or use `DEMO_MODE=true`.
- Image provider/model unavailable: change `IMAGE_MODEL` or `IMAGE_PROVIDER` in `.env` to a model currently offered by your Hugging Face account/provider.
- PDF contains replacement characters for non-Latin text: the current exporter uses FPDF's built-in Helvetica for portability. For full Unicode PDF output, add a Unicode TTF font and register it in `exporters.py`.

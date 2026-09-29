import traceback
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.exporters import save_pdf
from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image
from app.layout_builder import build_comic_layout
from app.schemas import ComicRequest

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
router = APIRouter()


def demo_outline(request: ComicRequest):
    from app.schemas import ComicOutline, PanelOutline
    return ComicOutline(
        panels=[
            PanelOutline(
                panel_number=i,
                title=[
                    "The Idea", "The Journey", "A Surprise",
                    "The Challenge", "The New Beginning"
                ][i - 1],
                scene_description=f"{request.character_name} explores {request.setting}.",
                image_prompt=(
                    f"{request.character_name} in {request.setting}, "
                    f"{request.art_style}, {request.tone}, clean comic illustration"
                ),
            )
            for i in range(1, settings.panels + 1)
        ]
    )


def demo_story(outline, request: ComicRequest):
    from app.schemas import ComicStory, PanelStory
    return ComicStory(
        panels=[
            PanelStory(
                panel_number=p.panel_number,
                title=p.title,
                scene_description=p.scene_description,
                caption=f"Something exciting is happening in {request.setting}.",
                narration=f"{request.character_name} takes the next step with courage.",
                dialogue=f"{request.character_name}: Let's see where this adventure leads!",
            )
            for p in outline.panels
        ]
    )


def generate_comic(request: ComicRequest):
    if settings.demo_mode:
        outline = demo_outline(request)
        story = demo_story(outline, request)
    else:
        outline = generate_outline(
            request.story_prompt,
            request.character_name,
            request.setting,
            request.tone,
            request.art_style,
        )
        story = generate_story(outline, request.character_name, request.tone)

    image_paths = [
        generate_image(panel.image_prompt, panel.panel_number)
        for panel in outline.panels
    ]
    layout = build_comic_layout(outline, story, image_paths)
    pdf_path, filename = save_pdf(layout)
    pdf_url = "/static/exports/" + filename
    return layout, pdf_url, filename


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": settings.app_name,
            "demo_mode": settings.demo_mode,
        },
    )


@router.post("/generate", response_class=HTMLResponse)
def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    payload = ComicRequest(
        story_prompt=story_prompt[:settings.max_prompt_chars],
        character_name=character_name,
        setting=setting,
        tone=tone,
        art_style=art_style,
    )

    try:
        layout, pdf_url, filename = generate_comic(payload)

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "app_name": settings.app_name,
                "layout": layout,
                "pdf_url": pdf_url,
                "filename": filename,
            },
        )

    except Exception as exc:
        import traceback

        print("\n========== COMICCRAFT ERROR ==========")
        traceback.print_exc()
        print("======================================\n")

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "app_name": settings.app_name,
                "demo_mode": settings.demo_mode,
                "error": str(exc),
                "form": payload.model_dump(),
            },
            status_code=500,
        )


@router.post("/generate-comic/json")
def generate_json(payload: ComicRequest):
    try:
        layout, pdf_url, filename = generate_comic(payload)
        return {
            "success": True,
            "panels": [panel.model_dump() for panel in layout],
            "pdf_url": pdf_url,
            "filename": filename,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/test-image")
def test_image(prompt: str = Form(...)):
    try:
        path = generate_image(prompt, 999)
        return {"success": True, "image_url": "/static/panels/" + Path(path).name}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/export-success", response_class=HTMLResponse)
def export_success(request: Request, filename: str = ""):
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={"app_name": settings.app_name, "filename": filename},
    )


@router.get("/health")
def health():
    return {
        "status": "ok",
        "demo_mode": settings.demo_mode,
        "gemini_configured": bool(settings.gemini_api_key),
        "image_backend": settings.image_backend,
        "hf_configured": bool(settings.hf_token),
    }

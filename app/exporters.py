from pathlib import Path
from datetime import datetime

from fpdf import FPDF

from app.config import settings
from app.schemas import ComicPanel


def _safe_text(value: str | None) -> str:
    """Convert text to a PDF-safe string."""
    if not value:
        return ""

    replacements = {
        "—": "-",
        "–": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "…": "...",
        "•": "-",
    }

    text = str(value)

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.encode("latin-1", "replace").decode("latin-1")


def save_pdf(panels: list[ComicPanel]):
    """Create and save the generated comic as a PDF."""

    export_dir = Path(settings.export_dir)
    export_dir.mkdir(parents=True, exist_ok=True)

    filename = f"comic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    output_path = export_dir / filename

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4",
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15,
    )

    page_width = 210
    left_margin = 15
    right_margin = 15
    text_width = page_width - left_margin - right_margin

    for panel in panels:

        pdf.add_page()

        # -------------------------
        # Panel title
        # -------------------------
        pdf.set_xy(left_margin, 15)

        pdf.set_font("Helvetica", "B", 16)

        title = _safe_text(
            f"Panel {panel.panel_number}: {panel.title}"
        )

        pdf.multi_cell(
            w=text_width,
            h=8,
            text=title,
        )

        # -------------------------
        # Image
        # -------------------------
        image_path = Path(panel.image_path)

        if image_path.exists():

            pdf.image(
                str(image_path),
                x=left_margin,
                y=40,
                w=text_width,
            )

        # -------------------------
        # Text section
        # -------------------------
        pdf.set_xy(left_margin, 165)

        pdf.set_font("Helvetica", "I", 10)

        scene = _safe_text(panel.scene_description)

        if scene:
            pdf.multi_cell(
                w=text_width,
                h=5,
                text=scene,
            )

        # -------------------------
        # Caption
        # -------------------------
        caption = _safe_text(panel.caption)

        if caption:

            pdf.set_x(left_margin)

            pdf.set_font(
                "Helvetica",
                "B",
                10,
            )

            pdf.multi_cell(
                w=text_width,
                h=5,
                text=f"Caption: {caption}",
            )

        # -------------------------
        # Narration
        # -------------------------
        narration = _safe_text(panel.narration)

        if narration:

            pdf.set_x(left_margin)

            pdf.set_font(
                "Helvetica",
                "",
                10,
            )

            pdf.multi_cell(
                w=text_width,
                h=5,
                text=f"Narration: {narration}",
            )

        # -------------------------
        # Dialogue
        # -------------------------
        dialogue = _safe_text(panel.dialogue)

        if dialogue:

            pdf.set_x(left_margin)

            pdf.set_font(
                "Helvetica",
                "I",
                10,
            )

            pdf.multi_cell(
                w=text_width,
                h=5,
                text=f"Dialogue: {dialogue}",
            )

    pdf.output(str(output_path))

    return str(output_path), filename
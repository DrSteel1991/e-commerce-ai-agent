"""
Generate policy PDFs from plain-text files in backend/documents/content/.

Run from rag-service (needs reportlab installed):

    cd backend/rag-service
    source .venv/bin/activate
    python -m app.scripts.generate_policy_pdfs
"""

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def _build_story(text: str, styles) -> list:
    story = []
    body = styles["BodyText"]
    heading = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        spaceAfter=12,
        spaceBefore=6,
    )

    blocks = [block.strip() for block in text.split("\n\n") if block.strip()]

    for index, block in enumerate(blocks):
        style = heading if index == 0 else body
        safe = block.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        safe = safe.replace("\n", "<br/>")
        story.append(Paragraph(safe, style))
        story.append(Spacer(1, 0.15 * inch))

    return story


def text_to_pdf(text_path: Path, pdf_path: Path) -> None:
    text = text_path.read_text(encoding="utf-8")
    styles = getSampleStyleSheet()

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch,
    )

    doc.build(_build_story(text, styles))


def main() -> None:
    project_root = Path(__file__).resolve().parents[3]
    content_dir = project_root / "documents" / "content"
    output_dir = project_root / "documents"

    if not content_dir.exists():
        raise FileNotFoundError(f"Content directory not found: {content_dir}")

    txt_files = sorted(content_dir.glob("*.txt"))

    if not txt_files:
        print("No .txt files found in documents/content/")
        return

    for text_path in txt_files:
        pdf_path = output_dir / f"{text_path.stem}.pdf"
        text_to_pdf(text_path, pdf_path)
        print(f"Created {pdf_path.name}")


if __name__ == "__main__":
    main()

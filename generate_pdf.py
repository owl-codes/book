#!/usr/bin/env python3
"""Generate a PDF from the book's markdown chapters using reportlab."""

import re
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.colors import Color
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, FrameBreak
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

CHAPTERS_DIR = Path(__file__).parent / "chapters"
OUTPUT = Path(__file__).parent / "The_Wildtongue_Chronicles.pdf"

CHAPTER_FILES = [
    "01-the-frequency.md",
    "02-the-laughing-man.md",
    "03-the-dive.md",
    "04-the-lawkeeper.md",
    "05-the-requiem.md",
    "06-the-old-guard.md",
    "07-the-forty-seventh.md",
    "08-the-frequency.md",
]

# Styles
BODY = ParagraphStyle(
    "Body",
    fontName="Times-Roman",
    fontSize=11.5,
    leading=16,
    alignment=TA_JUSTIFY,
    firstLineIndent=20,
    spaceBefore=2,
    spaceAfter=2,
)

BODY_NO_INDENT = ParagraphStyle(
    "BodyNoIndent",
    parent=BODY,
    firstLineIndent=0,
)

CHAPTER_TITLE = ParagraphStyle(
    "ChapterTitle",
    fontName="Times-Bold",
    fontSize=18,
    leading=24,
    alignment=TA_CENTER,
    spaceBefore=60,
    spaceAfter=30,
)

SCENE_BREAK = ParagraphStyle(
    "SceneBreak",
    fontName="Times-Roman",
    fontSize=12,
    leading=16,
    alignment=TA_CENTER,
    spaceBefore=16,
    spaceAfter=16,
    textColor=Color(0.47, 0.47, 0.47),
)

BOOK_TITLE = ParagraphStyle(
    "BookTitle",
    fontName="Times-Bold",
    fontSize=28,
    leading=34,
    alignment=TA_CENTER,
)

BOOK_SUBTITLE = ParagraphStyle(
    "BookSubtitle",
    fontName="Times-Italic",
    fontSize=16,
    leading=22,
    alignment=TA_CENTER,
    textColor=Color(0.4, 0.4, 0.4),
)

BOLD_LINE = ParagraphStyle(
    "BoldLine",
    fontName="Times-Bold",
    fontSize=11.5,
    leading=16,
    spaceBefore=6,
    spaceAfter=6,
)


def md_to_html(text):
    """Convert markdown inline formatting to reportlab-compatible HTML tags."""
    # ***bold+italic*** -> <b><i>...</i></b>
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', text)
    # **bold** -> <b>...</b>
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # *italic* -> <i>...</i>
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    return text


def add_page_number(canvas, doc):
    """Add page number footer."""
    if doc.page > 1:
        canvas.saveState()
        canvas.setFont("Times-Roman", 9)
        canvas.setFillColor(Color(0.6, 0.6, 0.6))
        canvas.drawCentredString(A4[0] / 2, 15 * mm, str(doc.page))
        canvas.restoreState()


def build_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=30 * mm,
        rightMargin=30 * mm,
        topMargin=25 * mm,
        bottomMargin=25 * mm,
    )

    story = []

    # --- Title page ---
    story.append(Spacer(1, 80 * mm))
    story.append(Paragraph("THE WILDTONGUE CHRONICLES", BOOK_TITLE))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph("Book One: The Choir of Erythis-3", BOOK_SUBTITLE))
    story.append(PageBreak())

    # --- Chapters ---
    for ch_idx, filename in enumerate(CHAPTER_FILES):
        filepath = CHAPTERS_DIR / filename
        md = filepath.read_text(encoding="utf-8")
        lines = md.split("\n")

        first_para_in_section = True

        for line in lines:
            stripped = line.strip()

            if not stripped:
                continue

            # Chapter heading
            if stripped.startswith("# "):
                heading = stripped[2:].upper()
                story.append(Paragraph(heading, CHAPTER_TITLE))
                first_para_in_section = True
                continue

            # Scene break
            if stripped == "---":
                story.append(Paragraph("*&nbsp;&nbsp;&nbsp;*&nbsp;&nbsp;&nbsp;*", SCENE_BREAK))
                first_para_in_section = True
                continue

            # Bold-only line
            bold_match = re.match(r"^\*\*(.+)\*\*$", stripped)
            if bold_match:
                story.append(Paragraph(bold_match.group(1), BOLD_LINE))
                first_para_in_section = True
                continue

            # Normal paragraph
            html = md_to_html(stripped)
            style = BODY_NO_INDENT if first_para_in_section else BODY
            story.append(Paragraph(html, style))
            first_para_in_section = False

        # Page break between chapters
        if ch_idx < len(CHAPTER_FILES) - 1:
            story.append(PageBreak())

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"Generated: {OUTPUT}")


if __name__ == "__main__":
    build_pdf()

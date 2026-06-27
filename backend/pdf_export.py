from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io


def build_resume_pdf(resume_text: str, job_title: str, company: str) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=1.8*cm,
        leftMargin=1.8*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm,
    )

    styles = getSampleStyleSheet()

    name_style = ParagraphStyle(
        "Name",
        fontSize=20,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1A1A2E"),
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    contact_style = ParagraphStyle(
        "Contact",
        fontSize=9,
        fontName="Helvetica",
        textColor=colors.HexColor("#5A5A5A"),
        alignment=TA_CENTER,
        spaceAfter=10,
    )
    section_style = ParagraphStyle(
        "Section",
        fontSize=11,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#2D5BFF"),
        spaceBefore=12,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "Body",
        fontSize=10,
        fontName="Helvetica",
        textColor=colors.HexColor("#1A1A1A"),
        leading=15,
        spaceAfter=3,
    )
    bullet_style = ParagraphStyle(
        "Bullet",
        fontSize=10,
        fontName="Helvetica",
        textColor=colors.HexColor("#1A1A1A"),
        leading=15,
        leftIndent=15,
        spaceAfter=2,
    )

    story = []
    lines = resume_text.split("\n")
    first_section = True

    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 0.15*cm))
            continue

        # Escape HTML
        line_escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        if line.startswith("===") and line.endswith("==="):
            section_name = line.strip("= ").title()
            if first_section:
                first_section = False
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#2D5BFF")))
            story.append(Paragraph(section_name.upper(), section_style))

        elif line.startswith("-") or line.startswith("•"):
            bullet_text = "• " + line.lstrip("-• ").strip()
            bullet_text = bullet_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(bullet_text, bullet_style))

        elif first_section and len(story) == 0:
            # First line = name
            story.append(Paragraph(line_escaped, name_style))

        elif first_section and len(story) <= 2:
            # Contact info
            story.append(Paragraph(line_escaped, contact_style))

        else:
            story.append(Paragraph(line_escaped, body_style))

    doc.build(story)
    return buf.getvalue()
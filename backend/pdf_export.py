from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import io


def build_resume_pdf(resume_text: str, job_title: str, company: str) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#1A1A2E"),
        spaceAfter=4,
        spaceBefore=10,
        fontSize=12,
        fontName="Helvetica-Bold",
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        spaceAfter=4,
    )

    story = []
    story.append(Paragraph(f"Resume — {job_title} at {company}", heading_style))
    story.append(Spacer(1, 0.3*cm))

    for line in resume_text.split("\n"):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 0.15*cm))
            continue
        if line.startswith("===") and line.endswith("==="):
            section_name = line.strip("= ").title()
            story.append(Spacer(1, 0.2*cm))
            story.append(Paragraph(section_name, heading_style))
        else:
            line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if line.startswith("-") or line.startswith("•"):
                line = "• " + line.lstrip("-• ").strip()
            story.append(Paragraph(line, body_style))

    doc.build(story)
    return buf.getvalue()
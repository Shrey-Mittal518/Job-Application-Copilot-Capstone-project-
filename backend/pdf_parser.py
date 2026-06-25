from pypdf import PdfReader
import io

def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()

def parse_resume_sections(raw_text: str) -> dict:
    sections = {
        "header": [],
        "experience": [],
        "education": [],
        "skills": [],
        "projects": [],
        "other": []
    }
    
    current = "header"
    
    for line in raw_text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        lower = stripped.lower()
        if any(k in lower for k in ["experience", "employment", "work history"]):
            current = "experience"
        elif any(k in lower for k in ["education", "academic", "qualification"]):
            current = "education"
        elif any(k in lower for k in ["skills", "technologies", "competencies"]):
            current = "skills"
        elif any(k in lower for k in ["projects", "portfolio"]):
            current = "projects"
        else:
            sections[current].append(stripped)
    
    return {k: "\n".join(v) for k, v in sections.items()}

def sections_to_plain(sections: dict) -> str:
    parts = []
    for section, content in sections.items():
        if content.strip():
            parts.append(f"=== {section.upper()} ===\n{content}")
    return "\n\n".join(parts)
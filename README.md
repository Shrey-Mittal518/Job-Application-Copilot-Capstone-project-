# Job Application Co-Pilot 🚀

A multi-agent AI system that turns your resume + job description into a complete application kit in under 60 seconds.

## What it does
Upload your resume PDF and paste a job description. The app runs 5 AI agents in sequence:
1. **Fit Analyst** — which requirements you meet, which you don't
2. **Resume Writer** — tailored rewrite with JD keywords woven in
3. **Cover Letter Writer** — 1-page, tone-matched to the company
4. **Interview Coach** — 10 Q&A pairs grounded in your resume
5. **ATS Scorer** — keyword density score + missing keywords

Plus: Voice mock interview, Salary negotiation coach, Diff view, Download as .docx/.pdf

## Tech Stack
- **Frontend:** Vanilla HTML + CSS + JS
- **Backend:** FastAPI + JWT auth
- **Database:** SQLite + SQLAlchemy + Alembic
- **AI:** Groq llama-3.3-70b-versatile (5 agents)
- **PDF:** pypdf
- **Exports:** python-docx, reportlab

## How to run locally

### Backend
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate      # Windows
pip install -r requirements.txt
cp .env.example .env         # Add your GROQ_API_KEY
alembic upgrade head
uvicorn main:app --reload
```
API runs at: http://127.0.0.1:8000
Swagger docs: http://127.0.0.1:8000/docs

### Frontend
Open `frontend/index.html` with Live Server (VS Code extension) or any static server.

## Environment Variables
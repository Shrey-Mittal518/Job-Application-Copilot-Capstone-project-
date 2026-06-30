# 🚀 Job Application Co-Pilot

> A multi-agent AI system that transforms your resume + job description into a complete, tailored application kit in under 60 seconds.

## 📌 Problem Statement

Applying for jobs is repetitive and exhausting. Every role demands 20+ minutes of tweaking — rewriting bullets, drafting cover letters, preparing interview answers. This app eliminates that grind using a 5-agent AI pipeline that produces four high-quality drafts instantly.

## ✨ Features

### Core
- 📄 **Resume PDF Upload** — parsed into structured sections using pypdf
- 🔗 **JD Input** — paste text or a URL (LinkedIn, Greenhouse, Lever, Workday auto-scraped)
- 🎯 **Fit Analysis** — which JD requirements you meet, miss, and should emphasise
- ✍️ **Resume Rewrite** — same roles, sharper bullets, JD keywords woven in
- ✉️ **Cover Letter** — 1-page, tone-matched to the company
- 🎤 **Interview Q&A Pack** — 10 questions + STAR answers grounded in your resume
- 🔀 **Diff View** — original vs rewritten resume side by side
- 📋 **Roles Dashboard** — manage all applications with status tracking

### Stretch Goals (all implemented)
- 📊 **ATS Scorer** — keyword density score + missing keywords list
- 🎙️ **Voice Mock Interview** — speak your answer, LLM grades and gives feedback
- 💰 **Salary Negotiation Coach** — get email + phone scripts for your specific offer
- 📅 **Follow-up Reminders** — auto-calculated 7-day follow-up date per application
- ⬇️ **Downloads** — cover letter as .docx, resume as PDF
- 🔄 **Regenerate** — re-run any single agent without rerunning the full pipeline

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vanilla HTML + CSS + JavaScript |
| Backend | FastAPI + Pydantic v2 + Uvicorn |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Database | SQLite + SQLAlchemy ORM + Alembic |
| AI Agents | Groq llama-3.3-70b-versatile (hand-rolled coordinator) |
| PDF Parse | pypdf |
| JD Scrape | requests + beautifulsoup4 |
| Exports | python-docx + reportlab |
| Deployment | Render (backend) |

## 🗄️ Database Schema

```
users
├── id, email, full_name, hashed_pw, created_at

roles
├── id, user_id (FK), job_title, company
├── jd_text, jd_url, original_resume
├── status (not_yet/applied/interviewed/rejected)
├── applied_date, follow_up_date, created_at

drafts
├── id, role_id (FK)
├── fit_analysis, resume_rewrite, cover_letter
├── interview_qa, ats_score, ats_missing_kw
├── salary_scripts, created_at, updated_at

revisions
├── id, draft_id (FK)
├── section, before_text, after_text, created_at
```

## 🤖 Agent Pipeline

```
User uploads Resume PDF + JD
          ↓
    FastAPI /applications (JWT protected)
          ↓
    Parse PDF → resume sections
    If URL → scrape JD with BeautifulSoup
          ↓
    Orchestrator (hand-rolled coordinator)
          ↓
    Agent 1: Fit Analyst (LLM)
          ↓ fit_analysis feeds all below
    Agent 2: Resume Writer
    Agent 3: Cover Letter Writer
    Agent 4: Interview Coach
    Agent 5: ATS Scorer
          ↓
    Persist to DB → Return to Frontend
```

## 📁 Project Structure

```
job-copilot/
├── README.md
├── backend/
│   ├── main.py              # FastAPI app entry point + CORS
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic v2 request/response schemas
│   ├── auth.py              # JWT auth + bcrypt password hashing
│   ├── database.py          # SQLAlchemy engine + session
│   ├── pdf_parser.py        # pypdf resume text extraction
│   ├── jd_scraper.py        # BeautifulSoup JD URL scraper
│   ├── docx_export.py       # python-docx cover letter export
│   ├── pdf_export.py        # reportlab resume PDF export
│   ├── requirements.txt
│   ├── .env.example
│   ├── agents/
│   │   └── pipeline.py      # 5 AI agents + orchestrator
│   ├── routes/
│   │   ├── auth.py          # /auth/register, /login, /me
│   │   ├── applications.py  # /applications CRUD + pipeline trigger
│   │   ├── drafts.py        # /drafts regenerate, download, salary, voice
│   │   └── scraper.py       # /scrape/jd URL scraper
│   └── migrations/          # Alembic migration files
└── frontend/
    ├── index.html           # Login + Register
    ├── css/
    │   └── style.css        # Full design system
    ├── js/
    │   └── app.js           # API client + shared utilities
    └── pages/
        ├── dashboard.html   # Roles list + stats + filters
        ├── new-application.html  # PDF upload + pipeline trigger
        └── artifacts.html   # 8-tab artifact viewer
```

## 🚀 Running Locally

### Prerequisites
- Python 3.11+
- A free Groq API key from [console.groq.com](https://console.groq.com)

### Backend Setup

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your GROQ_API_KEY to .env

# Run database migrations
alembic upgrade head

# Start the server
uvicorn main:app --reload
```

- API runs at: `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/docs`

### Frontend Setup
1. Open the `frontend/` folder in VS Code
2. Install the **Live Server** extension
3. Right-click `index.html` → **Open with Live Server**
4. App opens at `http://127.0.0.1:5500`

## 🔑 Environment Variables

Create a `.env` file in the `backend/` folder:

```
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your_super_secret_jwt_key
DATABASE_URL=sqlite:///./jobcopilot.db
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

## 📹 Demo Video
https://www.loom.com/share/b7696a671ccf4c0c896ac1c135373e5a

## 🖥️ Live Demo
https://job-copilot-frontend-ywl4.onrender.com


## 📊 Presentation
https://docs.google.com/presentation/d/1eaChDHFTTwYNlKPzJQ5ZUzjR3v5ao5E4JMZECcNwel4/edit?usp=sharing

---


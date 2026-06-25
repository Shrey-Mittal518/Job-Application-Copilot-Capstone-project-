import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

import httpx
client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
    http_client=httpx.Client()
)
MODEL = "llama-3.3-70b-versatile"


def _call(system: str, user: str, max_tokens: int = 2048) -> str:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=max_tokens,
        temperature=0.7,
    )
    return resp.choices[0].message.content.strip()


def agent_fit_analyst(resume: str, jd: str) -> str:
    system = """You are an expert career coach.
Analyse the resume against the job description and output:

## ✅ Requirements You Meet
- list each with evidence

## ❌ Gaps / Missing Requirements
- list what's missing

## 💡 What to Emphasise
- specific skills or achievements to highlight

## 📊 Overall Fit Score
X/10 — one sentence explanation"""

    user = f"RESUME:\n{resume}\n\nJOB DESCRIPTION:\n{jd}"
    return _call(system, user, max_tokens=1500)


def agent_resume_writer(resume: str, jd: str, fit_analysis: str) -> str:
    system = """You are a professional resume writer.
Rewrite the resume tailored to this job.
Rules:
- Keep same roles, companies, dates — never fabricate
- Sharper bullets with action verbs and metrics
- Weave in JD keywords naturally
- Output full resume with === SECTION === headers
- No commentary, just the resume"""

    user = f"RESUME:\n{resume}\n\nJOB DESCRIPTION:\n{jd}\n\nFIT ANALYSIS:\n{fit_analysis}"
    return _call(system, user, max_tokens=2000)


def agent_cover_letter(resume: str, jd: str, fit_analysis: str) -> str:
    system = """You are an expert cover letter writer.
Write a compelling 1-page cover letter (~300 words).
- No clichés like 'I am writing to express my interest'
- Strong opening with a specific achievement
- 2 body paragraphs mapping strengths to role needs
- Confident closing
- Use [Your Name], [Date], [Company] placeholders"""

    user = f"RESUME:\n{resume}\n\nJOB DESCRIPTION:\n{jd}\n\nFIT ANALYSIS:\n{fit_analysis}"
    return _call(system, user, max_tokens=1000)


def agent_interview_qa(resume: str, jd: str, fit_analysis: str) -> str:
    system = """You are an expert interview coach.
Generate exactly 10 interview questions and strong answers grounded in the resume.
Output as valid JSON array only, no markdown fences:
[
  {
    "question": "...",
    "category": "Behavioural",
    "answer": "..."
  }
]
Mix: 3 behavioural, 3 technical, 2 situational, 1 culture-fit, 1 weakness."""

    user = f"RESUME:\n{resume}\n\nJOB DESCRIPTION:\n{jd}\n\nFIT ANALYSIS:\n{fit_analysis}"
    return _call(system, user, max_tokens=3000)


def agent_ats_scorer(resume_rewrite: str, jd: str) -> dict:
    system = """You are an ATS expert.
Score the resume against the JD for keyword coverage.
Output valid JSON only, no markdown fences:
{
  "score": 78,
  "grade": "B+",
  "present_keywords": ["python", "fastapi"],
  "missing_keywords": ["kubernetes", "terraform"],
  "recommendations": ["Add Kubernetes if you have exposure"]
}"""

    user = f"REWRITTEN RESUME:\n{resume_rewrite}\n\nJOB DESCRIPTION:\n{jd}"
    raw = _call(system, user, max_tokens=800)
    try:
        raw = raw.strip().strip("```json").strip("```").strip()
        return json.loads(raw)
    except Exception:
        return {
            "score": 0,
            "grade": "N/A",
            "present_keywords": [],
            "missing_keywords": [],
            "recommendations": ["Could not parse. Try regenerating."]
        }


def agent_salary_coach(role_title: str, current_offer: str, location: str = "") -> str:
    system = """You are a salary negotiation coach.
Output:
## 📊 Market Context
## 💬 Email Script — Counter Offer
## 📞 Phone Script
## 🎯 Key Tactics
## ⚠️ What NOT to Do"""

    user = f"Role: {role_title}\nCurrent Offer: {current_offer}\nLocation: {location or 'Not specified'}"
    return _call(system, user, max_tokens=1500)


def agent_voice_grader(question: str, user_answer: str, resume_context: str) -> dict:
    system = """You are an interview coach grading a spoken answer.
Output valid JSON only, no markdown fences:
{
  "score": 7,
  "feedback": "...",
  "strengths": ["..."],
  "improvements": ["..."],
  "improved_answer": "..."
}"""

    user = f"QUESTION: {question}\nANSWER: {user_answer}\nRESUME CONTEXT: {resume_context[:1000]}"
    raw = _call(system, user, max_tokens=800)
    try:
        raw = raw.strip().strip("```json").strip("```").strip()
        return json.loads(raw)
    except Exception:
        return {
            "score": 5,
            "feedback": "Could not parse. Try again.",
            "strengths": [],
            "improvements": [],
            "improved_answer": ""
        }


def run_full_pipeline(resume_text: str, jd_text: str) -> dict:
    print("🔄 Agent 1: Fit Analysis...")
    fit_analysis = agent_fit_analyst(resume_text, jd_text)

    print("🔄 Agent 2: Resume Rewrite...")
    resume_rewrite = agent_resume_writer(resume_text, jd_text, fit_analysis)

    print("🔄 Agent 3: Cover Letter...")
    cover_letter = agent_cover_letter(resume_text, jd_text, fit_analysis)

    print("🔄 Agent 4: Interview Q&A...")
    interview_qa = agent_interview_qa(resume_text, jd_text, fit_analysis)

    print("🔄 Agent 5: ATS Score...")
    ats_result = agent_ats_scorer(resume_rewrite, jd_text)

    return {
        "fit_analysis": fit_analysis,
        "resume_rewrite": resume_rewrite,
        "cover_letter": cover_letter,
        "interview_qa": interview_qa,
        "ats_score": ats_result.get("score", 0),
        "ats_missing_kw": json.dumps(ats_result),
    }
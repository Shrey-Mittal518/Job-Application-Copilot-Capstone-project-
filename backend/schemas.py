from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from models import ApplicationStatus


# ── Auth ──────────────────────────────────────────────────────
class UserRegister(BaseModel):
    email: EmailStr
    full_name: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Roles ─────────────────────────────────────────────────────
class RoleCreate(BaseModel):
    job_title: str
    company: str
    jd_text: str
    jd_url: Optional[str] = None

class RoleStatusUpdate(BaseModel):
    status: ApplicationStatus

class RoleOut(BaseModel):
    id: int
    job_title: str
    company: str
    jd_url: Optional[str]
    status: ApplicationStatus
    applied_date: Optional[datetime]
    follow_up_date: Optional[datetime]
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Drafts ────────────────────────────────────────────────────
class DraftOut(BaseModel):
    id: int
    role_id: int
    fit_analysis: Optional[str]
    resume_rewrite: Optional[str]
    cover_letter: Optional[str]
    interview_qa: Optional[str]
    ats_score: Optional[int]
    ats_missing_kw: Optional[str]
    salary_scripts: Optional[str]
    updated_at: datetime
    model_config = {"from_attributes": True}


# ── Revisions ─────────────────────────────────────────────────
class RevisionOut(BaseModel):
    id: int
    section: str
    before_text: str
    after_text: str
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Pipeline ──────────────────────────────────────────────────
class RegenerateRequest(BaseModel):
    section: str

class SalaryRequest(BaseModel):
    role_title: str
    current_offer: str
    location: Optional[str] = None

class VoiceGradeRequest(BaseModel):
    question: str
    user_answer: str
    resume_context: str

class ScrapeRequest(BaseModel):
    url: str

class VoiceGradeOut(BaseModel):
    score: int
    feedback: str
    improved_answer: str
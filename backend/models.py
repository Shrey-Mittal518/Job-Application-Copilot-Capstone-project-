from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone
import enum

Base = declarative_base()

class ApplicationStatus(str, enum.Enum):
    not_yet     = "not_yet"
    applied     = "applied"
    interviewed = "interviewed"
    rejected    = "rejected"

class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True)
    email      = Column(String(255), unique=True, index=True, nullable=False)
    full_name  = Column(String(255), nullable=False)
    hashed_pw  = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    roles = relationship("Role", back_populates="user", cascade="all, delete-orphan")


class Role(Base):
    __tablename__ = "roles"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_title       = Column(String(255), nullable=False)
    company         = Column(String(255), nullable=False)
    jd_text         = Column(Text, nullable=False)
    jd_url          = Column(String(500), nullable=True)
    original_resume = Column(Text, nullable=False)
    status          = Column(SAEnum(ApplicationStatus), default=ApplicationStatus.not_yet)
    applied_date    = Column(DateTime, nullable=True)
    follow_up_date  = Column(DateTime, nullable=True)
    created_at      = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user   = relationship("User", back_populates="roles")
    drafts = relationship("Draft", back_populates="role", cascade="all, delete-orphan", uselist=False)


class Draft(Base):
    __tablename__ = "drafts"

    id             = Column(Integer, primary_key=True, index=True)
    role_id        = Column(Integer, ForeignKey("roles.id"), nullable=False, unique=True)
    fit_analysis   = Column(Text, nullable=True)
    resume_rewrite = Column(Text, nullable=True)
    cover_letter   = Column(Text, nullable=True)
    interview_qa   = Column(Text, nullable=True)
    ats_score      = Column(Integer, nullable=True)
    ats_missing_kw = Column(Text, nullable=True)
    salary_scripts = Column(Text, nullable=True)
    created_at     = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at     = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                            onupdate=lambda: datetime.now(timezone.utc))

    role      = relationship("Role", back_populates="drafts")
    revisions = relationship("Revision", back_populates="draft", cascade="all, delete-orphan")


class Revision(Base):
    __tablename__ = "revisions"

    id          = Column(Integer, primary_key=True, index=True)
    draft_id    = Column(Integer, ForeignKey("drafts.id"), nullable=False)
    section     = Column(String(50), nullable=False)
    before_text = Column(Text, nullable=False)
    after_text  = Column(Text, nullable=False)
    created_at  = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    draft = relationship("Draft", back_populates="revisions")
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json, io

from database import get_db
from auth import get_current_user
import models, schemas
from agents.pipeline import (
    agent_fit_analyst, agent_resume_writer, agent_cover_letter,
    agent_interview_qa, agent_ats_scorer, agent_salary_coach, agent_voice_grader
)
from docx_export import build_cover_letter_docx
from pdf_export import build_resume_pdf

router = APIRouter(prefix="/drafts", tags=["drafts"])


@router.get("/{role_id}", response_model=schemas.DraftOut)
def get_draft(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    draft = _get_draft_or_404(role_id, current_user.id, db)
    return draft


@router.post("/{role_id}/regenerate", response_model=schemas.DraftOut)
def regenerate_section(
    role_id: int,
    payload: schemas.RegenerateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    role  = _get_role_or_404(role_id, current_user.id, db)
    draft = _get_draft_or_404(role_id, current_user.id, db)

    section  = payload.section
    resume   = role.original_resume
    jd       = role.jd_text
    fit      = draft.fit_analysis or ""
    old_text = ""
    new_text = ""

    if section == "fit":
        old_text = draft.fit_analysis or ""
        new_text = agent_fit_analyst(resume, jd)
        draft.fit_analysis = new_text

    elif section == "resume":
        old_text = draft.resume_rewrite or ""
        new_text = agent_resume_writer(resume, jd, fit)
        draft.resume_rewrite = new_text

    elif section == "cover":
        old_text = draft.cover_letter or ""
        new_text = agent_cover_letter(resume, jd, fit)
        draft.cover_letter = new_text

    elif section == "interview":
        old_text = draft.interview_qa or ""
        new_text = agent_interview_qa(resume, jd, fit)
        draft.interview_qa = new_text

    elif section == "ats":
        old_text = draft.ats_missing_kw or ""
        result   = agent_ats_scorer(draft.resume_rewrite or resume, jd)
        new_text = json.dumps(result)
        draft.ats_score      = result.get("score", 0)
        draft.ats_missing_kw = new_text

    else:
        raise HTTPException(status_code=400, detail=f"Unknown section: {section}")

    # Save revision
    if old_text and new_text:
        rev = models.Revision(
            draft_id=draft.id,
            section=section,
            before_text=old_text,
            after_text=new_text,
        )
        db.add(rev)

    db.commit()
    db.refresh(draft)
    return draft


@router.get("/{role_id}/revisions", response_model=list[schemas.RevisionOut])
def get_revisions(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    draft = _get_draft_or_404(role_id, current_user.id, db)
    return (
        db.query(models.Revision)
        .filter(models.Revision.draft_id == draft.id)
        .order_by(models.Revision.created_at.desc())
        .all()
    )


@router.post("/{role_id}/salary")
def salary_coach(
    role_id: int,
    payload: schemas.SalaryRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    draft  = _get_draft_or_404(role_id, current_user.id, db)
    result = agent_salary_coach(
        role_title=payload.role_title,
        current_offer=payload.current_offer,
        location=payload.location or "",
    )
    draft.salary_scripts = result
    db.commit()
    return {"salary_scripts": result}


@router.post("/voice-grade", response_model=schemas.VoiceGradeOut)
def voice_grade(
    payload: schemas.VoiceGradeRequest,
    current_user: models.User = Depends(get_current_user),
):
    result = agent_voice_grader(
        question=payload.question,
        user_answer=payload.user_answer,
        resume_context=payload.resume_context,
    )
    return schemas.VoiceGradeOut(
        score=result.get("score", 5),
        feedback=result.get("feedback", ""),
        improved_answer=result.get("improved_answer", ""),
    )


@router.get("/{role_id}/download/cover-letter")
def download_cover_letter(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    role  = _get_role_or_404(role_id, current_user.id, db)
    draft = _get_draft_or_404(role_id, current_user.id, db)
    if not draft.cover_letter:
        raise HTTPException(status_code=404, detail="Cover letter not generated yet")

    docx_bytes = build_cover_letter_docx(draft.cover_letter, role.job_title, role.company)
    filename   = f"cover_letter_{role.company}_{role.job_title}.docx".replace(" ", "_")
    return StreamingResponse(
        io.BytesIO(docx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/{role_id}/download/resume")
def download_resume(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    role  = _get_role_or_404(role_id, current_user.id, db)
    draft = _get_draft_or_404(role_id, current_user.id, db)
    if not draft.resume_rewrite:
        raise HTTPException(status_code=404, detail="Resume not generated yet")

    pdf_bytes = build_resume_pdf(draft.resume_rewrite, role.job_title, role.company)
    filename  = f"resume_{role.company}_{role.job_title}.pdf".replace(" ", "_")
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


# ── Helpers ───────────────────────────────────────────────────
def _get_role_or_404(role_id: int, user_id: int, db: Session):
    role = db.query(models.Role).filter(
        models.Role.id == role_id,
        models.Role.user_id == user_id
    ).first()
    if not role:
        raise HTTPException(status_code=404, detail="Application not found")
    return role


def _get_draft_or_404(role_id: int, user_id: int, db: Session):
    role  = _get_role_or_404(role_id, user_id, db)
    draft = db.query(models.Draft).filter(models.Draft.role_id == role.id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return draft
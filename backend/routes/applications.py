from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta

from database import get_db
from auth import get_current_user
import models, schemas
from pdf_parser import extract_text_from_pdf, sections_to_plain, parse_resume_sections
from agents.pipeline import run_full_pipeline

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("/", response_model=schemas.RoleOut, status_code=201)
async def create_application(
    job_title:  str        = Form(...),
    company:    str        = Form(...),
    jd_text:    str        = Form(""),
    jd_url:     str        = Form(""),
    resume_pdf: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # 1. Parse PDF
    pdf_bytes  = await resume_pdf.read()
    raw_text   = extract_text_from_pdf(pdf_bytes)
    if not raw_text.strip():
        raise HTTPException(status_code=422, detail="Could not extract text from PDF")
    sections    = parse_resume_sections(raw_text)
    resume_text = sections_to_plain(sections)

    # 2. Handle JD
    final_jd  = jd_text.strip()
    final_url = jd_url.strip() or None
    if not final_jd:
        raise HTTPException(status_code=422, detail="Provide JD text")

    # 3. Save role
    role = models.Role(
        user_id=current_user.id,
        job_title=job_title,
        company=company,
        jd_text=final_jd,
        jd_url=final_url,
        original_resume=resume_text,
    )
    db.add(role)
    db.commit()
    db.refresh(role)

    # 4. Run pipeline
    try:
        outputs = run_full_pipeline(resume_text, final_jd)
    except Exception as e:
        db.delete(role)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

    # 5. Save drafts
    draft = models.Draft(
        role_id=role.id,
        fit_analysis=outputs["fit_analysis"],
        resume_rewrite=outputs["resume_rewrite"],
        cover_letter=outputs["cover_letter"],
        interview_qa=outputs["interview_qa"],
        ats_score=outputs["ats_score"],
        ats_missing_kw=outputs["ats_missing_kw"],
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)

    # 6. Save initial revision for diff view
    revision = models.Revision(
        draft_id=draft.id,
        section="resume",
        before_text=resume_text,
        after_text=outputs["resume_rewrite"],
    )
    db.add(revision)
    db.commit()

    return role


@router.get("/", response_model=list[schemas.RoleOut])
def list_applications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.Role)
        .filter(models.Role.user_id == current_user.id)
        .order_by(models.Role.created_at.desc())
        .all()
    )


@router.get("/{role_id}", response_model=schemas.RoleOut)
def get_application(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    role = db.query(models.Role).filter(
        models.Role.id == role_id,
        models.Role.user_id == current_user.id
    ).first()
    if not role:
        raise HTTPException(status_code=404, detail="Not found")
    return role


@router.patch("/{role_id}/status", response_model=schemas.RoleOut)
def update_status(
    role_id: int,
    payload: schemas.RoleStatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    role = db.query(models.Role).filter(
        models.Role.id == role_id,
        models.Role.user_id == current_user.id
    ).first()
    if not role:
        raise HTTPException(status_code=404, detail="Not found")
    role.status = payload.status
    if payload.status == models.ApplicationStatus.applied and not role.applied_date:
        role.applied_date   = datetime.now(timezone.utc)
        role.follow_up_date = datetime.now(timezone.utc) + timedelta(days=7)
    db.commit()
    db.refresh(role)
    return role


@router.delete("/{role_id}", status_code=204)
def delete_application(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    role = db.query(models.Role).filter(
        models.Role.id == role_id,
        models.Role.user_id == current_user.id
    ).first()
    if not role:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(role)
    db.commit()
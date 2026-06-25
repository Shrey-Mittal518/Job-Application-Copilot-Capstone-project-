from fastapi import APIRouter, HTTPException, Depends
from auth import get_current_user
import models, schemas
from jd_scraper import scrape_jd_from_url

router = APIRouter(prefix="/scrape", tags=["scraper"])


@router.post("/jd")
def scrape_jd(
    payload: schemas.ScrapeRequest,
    current_user: models.User = Depends(get_current_user),
):
    text = scrape_jd_from_url(payload.url)
    if not text:
        raise HTTPException(
            status_code=422,
            detail="Could not extract JD from URL. Paste the text manually."
        )
    return {"jd_text": text, "url": payload.url}
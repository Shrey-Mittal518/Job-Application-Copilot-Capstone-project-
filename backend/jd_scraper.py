import requests
from bs4 import BeautifulSoup
from typing import Optional

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}

def scrape_jd_from_url(url: str) -> Optional[str]:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception:
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove boilerplate
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    # Try known selectors
    selectors = [
        "div.description__text",      # LinkedIn
        "div#content",                 # Greenhouse
        "div.section-wrapper",         # Lever
        "article", "main",
        "div.job-description",
        "div.jobDescriptionContent",
    ]

    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            text = el.get_text(separator="\n").strip()
            if len(text) > 200:
                return _clean(text)

    # Fallback
    body = soup.find("body")
    if body:
        return _clean(body.get_text(separator="\n").strip()[:8000])

    return None


def _clean(text: str) -> str:
    import re
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

# extractor.py
from typing import Tuple
import trafilatura
import requests
from bs4 import BeautifulSoup

def extract_text_from_url(url: str) -> Tuple[str, str]:
    """
    Try trafilatura first. If it fails, do a fallback via BeautifulSoup.
    Returns (text, title)
    """
    # Try trafilatura (best extraction)
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        result = trafilatura.extract(downloaded, include_comments=False, include_tables=False, favor_precision=True)
        # trafilatura doesn't return title separately; parse it from html if possible
        title = None
        try:
            soup = BeautifulSoup(downloaded, "html.parser")
            title = soup.title.string.strip() if soup.title else None
        except Exception:
            title = None
        if result and len(result.strip()) > 100:
            return result, title or ""
    # fallback: simple requests + BeautifulSoup text extraction
    resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    # remove scripts/styles
    for s in soup(["script", "style", "noscript", "iframe"]):
        s.decompose()
    text = " ".join([p.get_text(separator=" ", strip=True) for p in soup.find_all(["p", "h1", "h2", "h3", "li"])])
    title = soup.title.string.strip() if soup.title else ""
    return text, title

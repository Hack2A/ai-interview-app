"""Feature 10: JD Manager — Add, store, and retrieve job descriptions.

Supports adding JDs from raw text or scraping from a URL.
"""
import hashlib
import logging
import re
from datetime import datetime

logger = logging.getLogger("JDManager")

# ── In-memory JD store ───────────────────────────────────────────────
_jd_store: list[dict] = []


def _make_id(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()[:8]


# ── Add from text ────────────────────────────────────────────────────

def add_jd_from_text(text: str, label: str = "") -> dict:
    """Store a job description from raw text.

    Args:
        text: Full JD text.
        label: Optional human-readable label (e.g. "Google SWE Intern").

    Returns:
        dict with id, label, word_count, added_at, and the text.
    """
    text = text.strip()
    if not text:
        return {"error": "JD text cannot be empty"}

    jd = {
        "id": _make_id(text),
        "label": label or f"JD-{len(_jd_store) + 1}",
        "text": text,
        "word_count": len(text.split()),
        "source": "text_input",
        "added_at": datetime.now().isoformat(),
    }
    _jd_store.append(jd)
    return jd


# ── Add from URL (web scraping) ──────────────────────────────────────

def add_jd_from_url(url: str) -> dict:
    """Scrape a job posting page and store the JD.

    Uses requests + BeautifulSoup to extract main text content.
    """
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        return {
            "error": "Missing dependencies. Run: pip install requests beautifulsoup4"
        }

    url = url.strip()
    if not url.startswith("http"):
        return {"error": f"Invalid URL: {url}"}

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove script/style
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        # Try common JD selectors first
        jd_text = ""
        selectors = [
            "div.job-description", "div.jobDescriptionContent",
            "section.job-details", "div.description", "article",
            "div.content", "main",
        ]
        for sel in selectors:
            el = soup.select_one(sel)
            if el and len(el.get_text(strip=True)) > 100:
                jd_text = el.get_text(separator="\n", strip=True)
                break

        if not jd_text:
            # Fallback: get all paragraph text
            paragraphs = soup.find_all(["p", "li", "div"])
            texts = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20]
            jd_text = "\n".join(texts)

        if len(jd_text) < 50:
            return {"error": "Could not extract meaningful JD text from URL"}

        jd = {
            "id": _make_id(jd_text),
            "label": soup.title.string.strip() if soup.title else url,
            "text": jd_text[:5000],
            "word_count": len(jd_text.split()),
            "source": "url_scrape",
            "url": url,
            "added_at": datetime.now().isoformat(),
        }
        _jd_store.append(jd)
        return jd

    except requests.RequestException as e:
        logger.error(f"URL fetch failed: {e}")
        return {"error": f"Failed to fetch URL: {e}"}
    except Exception as e:
        logger.error(f"JD scraping failed: {e}")
        return {"error": f"JD scraping failed: {e}"}


# ── Retrieval ────────────────────────────────────────────────────────

def list_jds() -> list[dict]:
    """List all stored JDs (without full text for brevity)."""
    return [
        {k: v for k, v in jd.items() if k != "text"}
        for jd in _jd_store
    ]


def get_jd(jd_id: str) -> dict | None:
    """Get a specific JD by ID."""
    for jd in _jd_store:
        if jd["id"] == jd_id:
            return jd
    return None


def get_jd_by_index(index: int) -> dict | None:
    """Get a JD by list index (0-based)."""
    if 0 <= index < len(_jd_store):
        return _jd_store[index]
    return None


def clear_jds() -> None:
    """Clear all stored JDs."""
    _jd_store.clear()

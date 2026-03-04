"""
Fetches full article text from newsletter URLs.
Falls back to the feed summary if the full page can't be scraped.
"""
import requests
from bs4 import BeautifulSoup

TIMEOUT = 15
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    )
}


def fetch_article_text(url: str, fallback_summary: str = "") -> str:
    """
    Attempt to fetch and extract readable body text from an article URL.
    Returns plain text suitable for summarisation.
    """
    try:
        resp = requests.get(url, timeout=TIMEOUT, headers=HEADERS)
        resp.raise_for_status()
    except Exception as e:
        print(f"[WARN] Could not fetch article {url}: {e}")
        return fallback_summary

    soup = BeautifulSoup(resp.text, "lxml")

    # Remove noise elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        tag.decompose()

    # Try common article containers in priority order
    for selector in [
        "article",
        '[class*="post-content"]',
        '[class*="article-body"]',
        '[class*="entry-content"]',
        "main",
    ]:
        el = soup.select_one(selector)
        if el:
            text = el.get_text(separator="\n", strip=True)
            if len(text) > 200:
                return text

    # Final fallback: all paragraph text
    paragraphs = soup.find_all("p")
    text = "\n".join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 40)
    return text or fallback_summary

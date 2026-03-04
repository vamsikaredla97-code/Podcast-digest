"""
Feed checker — polls all RSS feeds and returns new items published
within the last LOOKBACK_HOURS hours that haven't been seen before.
"""
import time
from datetime import datetime, timezone, timedelta
import feedparser
import requests
import state
from config.feeds import ALL_FEEDS

LOOKBACK_HOURS = 28
TIMEOUT = 15


def _parse_published(entry) -> datetime | None:
    """Return a timezone-aware UTC datetime from a feed entry, or None."""
    for field in ("published_parsed", "updated_parsed"):
        t = getattr(entry, field, None)
        if t:
            return datetime(*t[:6], tzinfo=timezone.utc)
    return None


def _item_id(feed_name: str, entry) -> str:
    """Stable unique ID for a feed entry."""
    return entry.get("id") or entry.get("link") or f"{feed_name}::{entry.get('title','')}"


def fetch_new_items(lookback_hours: int = LOOKBACK_HOURS) -> list[dict]:
    """
    Returns a list of new (unseen, recent) items across all feeds.

    Each item dict contains:
      feed_config  — the feed config dict from feeds.py
      title        — episode/article title
      url          — canonical link
      published    — datetime (UTC)
      summary      — raw feed summary/description
      item_id      — unique stable ID used for dedup
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
    new_items = []

    for feed_cfg in ALL_FEEDS:
        name = feed_cfg["name"]
        url = feed_cfg["rss_url"]

        try:
            resp = requests.get(
                url,
                timeout=TIMEOUT,
                # Browser-like UA required: Libsyn, Substack, and Stratechery
                # return HTTP 403 to generic/bot user agents.
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/121.0.0.0 Safari/537.36"
                    )
                },
            )
            resp.raise_for_status()
            parsed = feedparser.parse(resp.text)
        except Exception as e:
            print(f"[WARN] Could not fetch {name}: {e}")
            continue

        for entry in parsed.entries:
            published = _parse_published(entry)
            if published and published < cutoff:
                continue  # too old

            item_id = _item_id(name, entry)
            if state.is_seen(item_id):
                continue

            new_items.append(
                {
                    "feed_config": feed_cfg,
                    "title": entry.get("title", "Untitled"),
                    "url": entry.get("link", ""),
                    "published": published,
                    "summary": entry.get("summary", ""),
                    "item_id": item_id,
                }
            )

    return new_items

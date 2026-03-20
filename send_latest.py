#!/usr/bin/env python3
"""
One-shot script to immediately send the latest episode from one or more feeds,
bypassing the 28-hour deduplication window used by digest.py.

Usage:
    python send_latest.py                          # sends latest from all feeds in TARGETS
    python send_latest.py "The Peel"               # sends latest from a named feed
    python send_latest.py "The Peel" "Sourcery"    # sends latest from two named feeds

The episode is still marked as seen so the daily digest won't re-send it.
"""
import sys
import os
from dotenv import load_dotenv

load_dotenv()

import feedparser
import state
import summariser
import pdf_generator
import email_sender
import notion_logger
import transcript as transcript_mod

from config.feeds import ALL_FEEDS

# Default targets when run with no arguments
DEFAULT_TARGETS = ["The Peel", "Sourcery"]

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PodcastDigestBot/1.0)"}


def _fetch_latest_entry(rss_url: str) -> dict | None:
    feed = feedparser.parse(rss_url, request_headers=HEADERS)
    entries = feed.get("entries", [])
    return entries[0] if entries else None


def _find_feed_config(name: str) -> dict | None:
    name_lower = name.lower()
    for cfg in ALL_FEEDS:
        if (
            name_lower in cfg["name"].lower()
            or name_lower in cfg.get("short_name", "").lower()
        ):
            return cfg
    return None


def send_latest_podcast(cfg: dict) -> None:
    rss_url = cfg["rss_url"]
    podcast_name = cfg["name"]
    print(f"\n[LATEST] {podcast_name}")
    print(f"  Fetching feed: {rss_url}")

    entry = _fetch_latest_entry(rss_url)
    if not entry:
        print(f"  [ERROR] No entries found in feed.")
        return

    title = entry.get("title", "(no title)")
    article_url = entry.get("link", rss_url)
    summary_html = entry.get("summary", "")
    print(f"  Episode: {title}")
    print(f"  URL:     {article_url}")

    # Find YouTube link for transcript
    youtube_url = transcript_mod.search_youtube(f"{podcast_name} {title}")
    spotify_url = transcript_mod.search_spotify(podcast_name, title)
    link = spotify_url or youtube_url or article_url

    raw_transcript = None
    if youtube_url:
        print(f"  YouTube: {youtube_url}")
        raw_transcript = transcript_mod.get_transcript(youtube_url)
        if raw_transcript:
            print(f"  Transcript: {len(raw_transcript):,} chars fetched")
        else:
            print("  Transcript: not available — using feed summary")

    content_for_pdf = raw_transcript or summary_html or title

    summary = summariser.summarise_podcast(
        transcript=content_for_pdf,
        episode_title=title,
        podcast_name=podcast_name,
    )

    pdf_path = pdf_generator.generate_pdf(
        title=title,
        content=content_for_pdf,
        source_name=podcast_name,
    )
    print(f"  PDF: {pdf_path}")

    email_sender.send_podcast_email(
        podcast_name=podcast_name,
        episode_title=title,
        link=link,
        summary=summary,
        pdf_path=pdf_path,
    )

    notion_logger.log_item(
        title=title,
        publication=podcast_name,
        url=link,
        summary=summary,
        published=entry.get("published", ""),
        item_type="Podcast",
    )

    item_id = entry.get("id") or entry.get("link") or title
    state.mark_seen(item_id)
    print(f"  Done — emailed to {os.getenv('EMAIL_TO', '?')} and logged to Notion.")


def main() -> None:
    targets = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_TARGETS
    print(f"=== send_latest.py — targets: {targets} ===")

    for name in targets:
        cfg = _find_feed_config(name)
        if not cfg:
            print(f"\n[ERROR] No feed found matching '{name}'. Check config/feeds.py.")
            continue
        if cfg["type"] == "podcast":
            send_latest_podcast(cfg)
        else:
            print(f"\n[SKIP] '{cfg['name']}' is a newsletter — send_latest only supports podcasts.")


if __name__ == "__main__":
    main()

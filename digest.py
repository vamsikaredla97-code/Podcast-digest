#!/usr/bin/env python3
"""
Main digest orchestrator.

Checks all feeds, processes new items, generates AI summaries,
creates PDFs, emails them with attachments, and logs to Notion.

Run manually:  python digest.py
Scheduled:     cron runs this at 07:00 daily (see setup_cron.py)
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

import state
import feed_checker
import summariser
import pdf_generator
import email_sender
import notion_logger
import transcript as transcript_mod
import article_fetcher


def process_podcast(item: dict) -> None:
    cfg = item["feed_config"]
    title = item["title"]
    podcast_name = cfg["name"]
    article_url = item["url"]

    print(f"\n[PODCAST] {podcast_name} — {title}")

    # 1. Find Spotify link (preferred), fall back to YouTube, then RSS URL
    spotify_url = transcript_mod.search_spotify(podcast_name, title)
    youtube_url = transcript_mod.search_youtube(f"{podcast_name} {title}")
    link = spotify_url or youtube_url or article_url
    print(f"  Link: {link}")

    # 2. Fetch transcript from YouTube via Supadata API
    raw_transcript = None
    if youtube_url:
        raw_transcript = transcript_mod.get_transcript(youtube_url)

    content_for_pdf = raw_transcript or item["summary"] or title

    # 3. Summarise
    summary = summariser.summarise_podcast(
        transcript=content_for_pdf,
        episode_title=title,
        podcast_name=podcast_name,
    )

    # 4. Generate PDF of full transcript / content
    pdf_path = pdf_generator.generate_pdf(
        title=title,
        content=content_for_pdf,
        source_name=podcast_name,
    )
    print(f"  PDF: {pdf_path}")

    # 5. Send email with summary + PDF attachment
    email_sender.send_podcast_email(
        podcast_name=podcast_name,
        episode_title=title,
        link=link,
        summary=summary,
        pdf_path=pdf_path,
    )

    # 6. Log to Notion
    notion_logger.log_item(
        title=title,
        publication=podcast_name,
        url=link,
        summary=summary,
        published=item["published"],
        item_type="Podcast",
    )

    # 7. Mark seen
    state.mark_seen(item["item_id"])


def process_newsletter(item: dict) -> None:
    cfg = item["feed_config"]
    title = item["title"]
    publication = cfg["name"]
    author = cfg.get("author", "")
    article_url = item["url"]

    print(f"\n[NEWSLETTER] {publication} — {title}")

    # 1. Fetch full article text
    article_text = article_fetcher.fetch_article_text(article_url, item["summary"])

    # 2. Summarise
    synopsis = summariser.summarise_newsletter(
        article_text=article_text,
        title=title,
        publication=publication,
    )

    # 3. Generate PDF of full article
    pdf_path = pdf_generator.generate_pdf(
        title=title,
        content=article_text,
        source_name=publication,
    )
    print(f"  PDF: {pdf_path}")

    # 4. Send email with synopsis + PDF attachment
    email_sender.send_newsletter_email(
        publication=publication,
        author=author,
        article_title=title,
        article_url=article_url,
        synopsis=synopsis,
        pdf_path=pdf_path,
    )

    # 5. Log to Notion
    notion_logger.log_item(
        title=title,
        publication=publication,
        url=article_url,
        summary=synopsis,
        published=item["published"],
        item_type="Newsletter",
    )

    # 6. Mark seen
    state.mark_seen(item["item_id"])


def run_digest() -> None:
    print("=== Podcast & Newsletter Daily Digest ===")
    print("Fetching new items from all feeds...\n")

    new_items = feed_checker.fetch_new_items()

    if not new_items:
        print("No new items found. All caught up!")
        return

    podcasts = [i for i in new_items if i["feed_config"]["type"] == "podcast"]
    newsletters = [i for i in new_items if i["feed_config"]["type"] == "newsletter"]

    print(f"Found {len(podcasts)} new podcast episode(s) and {len(newsletters)} new newsletter(s).")

    for item in podcasts:
        try:
            process_podcast(item)
        except Exception as e:
            print(f"[ERROR] Failed to process podcast {item['title']}: {e}")

    for item in newsletters:
        try:
            process_newsletter(item)
        except Exception as e:
            print(f"[ERROR] Failed to process newsletter {item['title']}: {e}")

    # Send daily summary email
    email_sender.send_daily_summary_email(len(podcasts), len(newsletters))
    print(f"\n✅ Done. {len(podcasts)} podcast(s), {len(newsletters)} newsletter(s) emailed to {os.getenv('EMAIL_TO', '?')}.")


if __name__ == "__main__":
    run_digest()

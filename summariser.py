"""
Summariser — converts raw transcript or article text into a structured
email-optimised summary using Claude claude-sonnet-4-6.
"""
import os
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))

PODCAST_SYSTEM = """You are a concise briefing writer. Given a podcast episode transcript, produce a
clean bullet-point summary suitable for an email. Rules:
- Synthesis only: frameworks, mental models, key metrics, chronology — in your own words.
- Use plain-text formatting: each bullet starts with "- " followed by a bold header in the form "**Topic**: content".
- Numbers over adjectives. Company names and specific metrics required.
- Include 1-2 memorable quotes, clearly marked as quotes with quotation marks.
- No editorialising. No filler. No transcript dumps.
- Return 4–6 bullet points, each structured as: "- **Bold Header**: 2–3 lines of substance."
- Keep the whole summary under 400 words."""

NEWSLETTER_SYSTEM = """You are a concise briefing writer. Given a newsletter article, produce a
clean bullet-point synopsis suitable for an email. Rules:
- Synthesis only: major themes, data points, frameworks — in your own words.
- Use plain-text formatting: each bullet starts with "- " followed by a bold header in the form "**Topic**: content".
- Numbers over adjectives. Company names and specific metrics required.
- No editorialising. No filler.
- Return 3–5 bullet points, each structured as: "- **Bold Header**: 2–3 lines."
- Keep the whole synopsis under 300 words."""


def summarise_podcast(transcript: str, episode_title: str, podcast_name: str) -> str:
    prompt = (
        f"Podcast: {podcast_name}\n"
        f"Episode: {episode_title}\n\n"
        f"Transcript:\n{transcript[:12000]}"  # cap tokens
    )
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=700,
        system=PODCAST_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()


def summarise_newsletter(article_text: str, title: str, publication: str) -> str:
    prompt = (
        f"Publication: {publication}\n"
        f"Title: {title}\n\n"
        f"Article:\n{article_text[:12000]}"
    )
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        system=NEWSLETTER_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()

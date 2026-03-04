"""
WhatsApp message sender via Twilio.
Sends one message per item (not a combined digest).
"""
import os
from twilio.rest import Client

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
WHATSAPP_TO = os.getenv("WHATSAPP_TO", "")


def _client() -> Client:
    return Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def send_message(body: str, media_url: str | None = None) -> str:
    """
    Send a WhatsApp message. Returns the Twilio message SID.
    media_url: publicly accessible URL to a PDF (optional).
    """
    kwargs = {
        "from_": TWILIO_FROM,
        "to": WHATSAPP_TO,
        "body": body,
    }
    if media_url:
        kwargs["media_url"] = [media_url]

    msg = _client().messages.create(**kwargs)
    return msg.sid


def format_podcast_message(
    podcast_name: str,
    episode_title: str,
    link: str,
    guest_name: str,
    guest_role: str,
    guest_bio: str,
    summary: str,
    pdf_attached: bool = True,
) -> str:
    lines = [
        f"🎙️ *{podcast_name}*",
        f'"{episode_title}"',
        f"🔗 {link}",
        f"Guest: *{guest_name}*, {guest_role} — {guest_bio}",
        "",
        "*Key points:*",
        summary,
    ]
    if pdf_attached:
        lines.append("\n📎 Transcript PDF attached")
    return "\n".join(lines)


def format_newsletter_message(
    publication: str,
    author: str,
    article_title: str,
    article_url: str,
    context: str,
    synopsis: str,
    pdf_attached: bool = True,
) -> str:
    lines = [
        f"📝 *{publication}* ({author})",
        f'"{article_title}"',
        f"🔗 {article_url}",
        f"Context: {context}",
        "",
        "*Synopsis:*",
        synopsis,
    ]
    if pdf_attached:
        lines.append("\n📎 Article PDF attached")
    return "\n".join(lines)


def send_daily_summary(podcast_count: int, newsletter_count: int) -> None:
    send_message(f"✅ That's {podcast_count} podcast episode{'s' if podcast_count != 1 else ''} for today.")
    send_message(f"✅ That's {newsletter_count} newsletter{'s' if newsletter_count != 1 else ''} for today.")

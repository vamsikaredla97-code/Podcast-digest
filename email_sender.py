"""
Email sender for the daily podcast & newsletter digest.

Sends one HTML email per item with the summary in the body and the PDF attached.
Uses SMTP — works with Gmail (App Password), Outlook, or any SMTP relay.

Required .env keys:
    SMTP_HOST       e.g. smtp.gmail.com
    SMTP_PORT       587 (TLS) or 465 (SSL)
    SMTP_USER       your sending address
    SMTP_PASSWORD   Gmail App Password or SMTP credential
    EMAIL_TO        recipient address (vamsikaredla97@gmail.com)
    EMAIL_FROM      display address (defaults to SMTP_USER)
"""
import os
import smtplib
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_TO = os.getenv("EMAIL_TO", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "") or SMTP_USER


# ── HTML template helpers ──────────────────────────────────────────────────────

_HTML_BASE = """\
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          color: #1a1a1a; max-width: 680px; margin: 0 auto; padding: 24px; }}
  .header {{ background: {header_color}; border-radius: 10px;
             padding: 20px 24px; margin-bottom: 24px; }}
  .header h1 {{ margin: 0; font-size: 22px; color: #fff; }}
  .header p  {{ margin: 6px 0 0; color: rgba(255,255,255,0.85); font-size: 14px; }}
  .meta {{ background: #f5f5f7; border-radius: 8px; padding: 14px 18px;
           font-size: 13px; color: #555; margin-bottom: 20px; line-height: 1.8; }}
  .meta a {{ color: #0071e3; text-decoration: none; }}
  .summary {{ font-size: 15px; line-height: 1.75; }}
  .summary ul {{ padding-left: 20px; }}
  .summary li {{ margin-bottom: 10px; }}
  .summary b  {{ color: #1a1a1a; }}
  .pdf-note {{ margin-top: 20px; font-size: 13px; color: #888; }}
  .footer {{ margin-top: 32px; font-size: 12px; color: #aaa; border-top: 1px solid #eee;
             padding-top: 14px; }}
</style>
</head>
<body>
{body}
<div class="footer">Daily Digest · Sent {today} · Powered by Claude + Supadata</div>
</body>
</html>
"""


def _summary_to_html(summary: str) -> str:
    """Convert plain-text bullet summary into HTML <ul> list."""
    lines = summary.strip().split("\n")
    html_lines = []
    in_list = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append("<br>")
            continue
        if stripped.startswith(("- ", "• ", "* ")):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{stripped[2:]}</li>")
        elif stripped.startswith(("**", "__")):
            # Bold header line
            clean = stripped.strip("*_")
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<p><b>{clean}</b></p>")
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<p>{stripped}</p>")
    if in_list:
        html_lines.append("</ul>")
    return "\n".join(html_lines)


def _attach_pdf(msg: MIMEMultipart, pdf_path: str) -> None:
    path = Path(pdf_path)
    if not path.exists():
        return
    with open(path, "rb") as f:
        part = MIMEBase("application", "pdf")
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        "attachment",
        filename=path.name,
    )
    msg.attach(part)


def _send(msg: MIMEMultipart) -> None:
    """Connect to SMTP and send."""
    if not SMTP_USER or not SMTP_PASSWORD or not EMAIL_TO:
        print("[WARN] Email credentials not configured — skipping send.")
        return
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())


# ── Public send functions ──────────────────────────────────────────────────────

def send_podcast_email(
    podcast_name: str,
    episode_title: str,
    link: str,
    summary: str,
    pdf_path: str | None = None,
) -> None:
    """Send one email for a podcast episode with summary + optional PDF."""
    today_str = date.today().strftime("%B %-d, %Y")
    subject = f"[Podcast] {podcast_name}: {episode_title}"

    meta_html = f"""\
<div class="meta">
  <b>Podcast:</b> {podcast_name}<br>
  <b>Episode:</b> {episode_title}<br>
  <b>Link:</b> <a href="{link}">{link}</a><br>
  <b>Date:</b> {today_str}
</div>"""

    summary_html = f'<div class="summary">{_summary_to_html(summary)}</div>'
    pdf_note = '<p class="pdf-note">📎 Full transcript PDF attached.</p>' if pdf_path else ""

    body = f"""\
<div class="header" style="background:#1c2b4a;">
  <h1>🎙️ {podcast_name}</h1>
  <p>{episode_title}</p>
</div>
{meta_html}
{summary_html}
{pdf_note}"""

    html = _HTML_BASE.format(body=body, header_color="#1c2b4a", today=today_str)

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg.attach(MIMEText(html, "html"))
    if pdf_path:
        _attach_pdf(msg, pdf_path)

    _send(msg)
    print(f"  Email sent → {EMAIL_TO}")


def send_newsletter_email(
    publication: str,
    author: str,
    article_title: str,
    article_url: str,
    synopsis: str,
    pdf_path: str | None = None,
) -> None:
    """Send one email for a newsletter article with synopsis + optional PDF."""
    today_str = date.today().strftime("%B %-d, %Y")
    subject = f"[Newsletter] {publication}: {article_title}"

    byline = f" by {author}" if author else ""
    meta_html = f"""\
<div class="meta">
  <b>Publication:</b> {publication}{byline}<br>
  <b>Article:</b> {article_title}<br>
  <b>Link:</b> <a href="{article_url}">{article_url}</a><br>
  <b>Date:</b> {today_str}
</div>"""

    synopsis_html = f'<div class="summary">{_summary_to_html(synopsis)}</div>'
    pdf_note = '<p class="pdf-note">📎 Full article PDF attached.</p>' if pdf_path else ""

    body = f"""\
<div class="header" style="background:#1a3a2a;">
  <h1>📝 {publication}</h1>
  <p>{article_title}</p>
</div>
{meta_html}
{synopsis_html}
{pdf_note}"""

    html = _HTML_BASE.format(body=body, header_color="#1a3a2a", today=today_str)

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg.attach(MIMEText(html, "html"))
    if pdf_path:
        _attach_pdf(msg, pdf_path)

    _send(msg)
    print(f"  Email sent → {EMAIL_TO}")


def send_combined_podcast_email(
    episodes: list[dict],
) -> None:
    """
    Send all of today's podcast episodes in a single email.

    Each dict in `episodes` must have:
        podcast_name, episode_title, link, summary, pdf_path (str | None)

    All PDFs are attached to the same message. Each episode gets its own
    full header + meta block + summary section — nothing is compressed.
    """
    today_str = date.today().strftime("%B %-d, %Y")
    names = ", ".join(e["podcast_name"] for e in episodes)
    subject = f"[Podcasts] {today_str} — {len(episodes)} episodes"

    sections = []
    for i, ep in enumerate(episodes):
        divider = '<hr style="border:none;border-top:1px solid #eee;margin:32px 0;">' if i > 0 else ""
        meta_html = f"""\
<div class="meta">
  <b>Podcast:</b> {ep['podcast_name']}<br>
  <b>Episode:</b> {ep['episode_title']}<br>
  <b>Link:</b> <a href="{ep['link']}">{ep['link']}</a><br>
  <b>Date:</b> {today_str}
</div>"""
        summary_html = f'<div class="summary">{_summary_to_html(ep["summary"])}</div>'
        pdf_note = '<p class="pdf-note">📎 Full transcript PDF attached.</p>' if ep.get("pdf_path") else ""
        sections.append(f"""\
{divider}
<div class="header" style="background:#1c2b4a;">
  <h1>🎙️ {ep['podcast_name']}</h1>
  <p>{ep['episode_title']}</p>
</div>
{meta_html}
{summary_html}
{pdf_note}""")

    html = _HTML_BASE.format(
        body="\n".join(sections),
        header_color="#1c2b4a",
        today=today_str,
    )

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg.attach(MIMEText(html, "html"))
    for ep in episodes:
        if ep.get("pdf_path"):
            _attach_pdf(msg, ep["pdf_path"])

    _send(msg)
    print(f"  Combined email ({len(episodes)} episodes) sent → {EMAIL_TO}")


def send_daily_summary_email(podcast_count: int, newsletter_count: int) -> None:
    """Send a brief end-of-run summary email."""
    today_str = date.today().strftime("%B %-d, %Y")
    subject = f"✅ Daily Digest Complete — {today_str}"
    body_text = (
        f"Today's digest is complete.\n\n"
        f"  🎙️  {podcast_count} podcast episode{'s' if podcast_count != 1 else ''}\n"
        f"  📝  {newsletter_count} newsletter{'s' if newsletter_count != 1 else ''}\n\n"
        f"Check your inbox for individual summaries with PDF attachments."
    )
    body_html = f"""\
<div class="header" style="background:#2d2d2d;">
  <h1>✅ Daily Digest — {today_str}</h1>
</div>
<div class="summary">
  <p>🎙️ &nbsp;<b>{podcast_count}</b> podcast episode{'s' if podcast_count != 1 else ''}</p>
  <p>📝 &nbsp;<b>{newsletter_count}</b> newsletter{'s' if newsletter_count != 1 else ''}</p>
  <p style="color:#888; font-size:13px;">
    Individual summaries with PDF attachments have been sent separately.
  </p>
</div>"""
    html = _HTML_BASE.format(body=body_html, header_color="#2d2d2d", today=today_str)

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg.attach(MIMEText(html, "html"))
    _send(msg)

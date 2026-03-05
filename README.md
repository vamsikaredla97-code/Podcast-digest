# Podcast & Newsletter Daily Digest

Automated daily digest delivered to **vamsikaredla97@gmail.com** every morning at 07:00.

For each new **podcast episode**:
1. Finds the YouTube version and fetches the full transcript via **Supadata API**
2. Writes a bullet-point summary (key frameworks, metrics, memorable quotes) using **Claude AI**
3. Generates a **PDF** of the full transcript
4. Emails the summary with the PDF attached

For each new **newsletter article**:
1. Fetches the full article from the RSS feed
2. Writes a bullet-point summary in the same style
3. Generates a **PDF** of the full article
4. Emails the summary with the PDF attached

Everything is also logged to a **Notion database** (Title, Publication, URL, Summary, Date, Type).

---

## Feeds configured out of the box

### Podcasts
| Show | Host |
|------|------|
| The Twenty Minute VC (20VC) | Harry Stebbings |
| Lenny's Podcast | Lenny Rachitsky |
| All-In Podcast | Chamath, Jason, Sacks, Friedberg |
| Acquired | Ben Gilbert & David Rosenthal |
| My First Million | Sam Parr & Shaan Puri |
| Lex Fridman Podcast | Lex Fridman |
| How I Built This | Guy Raz |

### Newsletters
| Newsletter | Author |
|------------|--------|
| Not Boring | Packy McCormick |
| The Generalist | Mario Gabriele |
| Morning Brew | Morning Brew |
| The Hustle | The Hustle |
| TLDR Newsletter | TLDR |
| Stratechery | Ben Thompson |

To add or remove feeds, edit `config/feeds.py` and re-run `python validate_feeds.py`.

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Fill in `.env`

```bash
cp .env.example .env
```

| Variable | Where to get it |
|---|---|
| `SMTP_HOST` | `smtp.gmail.com` for Gmail |
| `SMTP_PORT` | `587` |
| `SMTP_USER` | Your Gmail address |
| `SMTP_PASSWORD` | [Gmail App Password](https://myaccount.google.com/apppasswords) — 16-char password, not your login password |
| `EMAIL_TO` | `vamsikaredla97@gmail.com` |
| `EMAIL_FROM` | Same as `SMTP_USER` |
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) → API Keys |
| `SUPADATA_API_KEY` | [supadata.ai](https://supadata.ai) → Dashboard |
| `NOTION_TOKEN` | [notion.so/my-integrations](https://www.notion.so/my-integrations) |
| `NOTION_DATABASE_ID` | From your Notion database URL |
| `YOUTUBE_API_KEY` | [Google Cloud Console](https://console.cloud.google.com) → YouTube Data API v3 *(recommended)* |
| `SPOTIFY_CLIENT_ID/SECRET` | [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard) *(optional)* |

### 3. Create the Notion database

Create a new Notion database with these exact properties:

| Property | Type |
|----------|------|
| Title | Title |
| Publication | Text |
| URL | URL |
| Summary | Text |
| Date | Date |
| Type | Select (`Podcast`, `Newsletter`) |

Share the database with your integration, then copy the database ID from the URL
(the 32-character string in `notion.so/<DATABASE_ID>?v=...`).

### 4. Validate feeds

```bash
python validate_feeds.py
```

### 5. Test a manual run

```bash
python digest.py
```

Check your inbox — you'll get one email per new item plus a summary email.

### 6. Install the daily cron job (07:00)

```bash
python setup_cron.py install
```

```bash
python setup_cron.py show    # view current crontab
python setup_cron.py remove  # uninstall
```

---

## Project structure

```
digest.py            — Main orchestrator (entry point)
setup_cron.py        — Install/remove daily cron job
validate_feeds.py    — One-time feed validation

config/
  feeds.py           — All RSS feed URLs — edit to add your own

feed_checker.py      — Polls feeds, filters by 28-hour window
state.py             — Deduplication (.digest_state.json)
transcript.py        — Supadata API transcript fetch + YouTube/Spotify link lookup
article_fetcher.py   — Full-text scraper for newsletter articles
summariser.py        — Claude AI summaries
pdf_generator.py     — PDF generation (fpdf2)
email_sender.py      — SMTP email with HTML body + PDF attachment
notion_logger.py     — Notion database logger
```

## Credentials summary

| Service | Required | Purpose |
|---------|----------|---------|
| Gmail SMTP | ✅ Yes | Sending emails |
| Anthropic | ✅ Yes | AI summaries |
| Supadata | ✅ Yes | YouTube transcripts |
| Notion | ✅ Yes | Digest log database |
| YouTube Data API | ⚡ Recommended | Episode link lookup |
| Spotify API | Optional | Spotify episode links |

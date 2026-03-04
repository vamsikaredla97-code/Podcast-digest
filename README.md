# Podcast & Newsletter Daily Digest

Automated morning digest that checks RSS feeds, summarises new episodes and articles, sends individual WhatsApp messages, and logs everything to Notion.

## What it does

- **07:00 daily** — checks all feeds for items published in the last 28 hours
- **Podcasts**: finds Spotify link → fetches YouTube transcript → Claude summary → PDF → WhatsApp
- **Newsletters**: fetches full article → Claude summary → PDF → WhatsApp
- **Notion log**: every item appended to a Notion database (Title, Publication, URL, Summary, Date, Type)
- **Deduplication**: state file prevents sending the same item twice

## Sources

| Source | Type | Feed |
|--------|------|------|
| The Twenty Minute VC | Podcast | `feeds.megaphone.fm/twentyminutevc` |
| Lenny's Podcast | Podcast | `lennyspodcast.com/feed/` |
| All-In Podcast | Podcast | `feeds.megaphone.fm/all-in-with-chamath-...` |
| Stratechery | Newsletter | `stratechery.com/feed/` |
| Not Boring | Newsletter | `notboring.co/feed` |
| The Generalist | Newsletter | `generalist.com/feed` |

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure secrets
```bash
cp .env.example .env
# Edit .env with your credentials
```

Required credentials:
- **Twilio**: Account SID, Auth Token, WhatsApp sandbox number
- **Notion**: Integration token + database ID
- **Anthropic**: API key (for Claude summaries)
- **YouTube Data API** (optional but recommended for transcripts)
- **Spotify API** (optional, for Spotify links)

### 3. Create the Notion database
In Notion, create a database with these properties:
- `Title` — Title
- `Publication` — Text
- `URL` — URL
- `Summary` — Text
- `Date` — Date
- `Type` — Select (options: Podcast, Newsletter)

Share it with your Notion integration, then copy the database ID into `.env`.

### 4. Validate feeds
```bash
python validate_feeds.py
```

### 5. Install cron job (07:00 daily)
```bash
python setup_cron.py install
```

### 6. Test manually
```bash
python digest.py
```

## File structure

```
digest.py           — Main orchestrator (entry point)
feed_checker.py     — RSS polling + deduplication logic
state.py            — Seen-item state (.digest_state.json)
summariser.py       — Claude-powered summarisation
transcript.py       — YouTube transcript + Spotify link lookup
article_fetcher.py  — Full article text scraping
pdf_generator.py    — PDF creation (fpdf2)
whatsapp_sender.py  — Twilio WhatsApp sender + message formatters
notion_logger.py    — Notion database appender
validate_feeds.py   — One-shot feed URL validator
setup_cron.py       — Cron job installer/remover
config/feeds.py     — All RSS URLs + feed metadata
```

## Updating feed URLs

All RSS URLs live in `config/feeds.py`. Edit there and re-run `python validate_feeds.py` to confirm.

## WhatsApp sandbox note

Twilio's WhatsApp sandbox requires recipients to opt in first. In production, apply for a Twilio WhatsApp Business number and update `TWILIO_WHATSAPP_FROM` in `.env`.

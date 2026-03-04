"""
Notion database logger.
Appends one row per digest item to the configured Notion database.

Database must have these properties:
  Title       (title)
  Publication (rich_text)
  URL         (url)
  Summary     (rich_text)
  Date        (date)
  Type        (select) — "Podcast" | "Newsletter"
"""
import os
from datetime import datetime, timezone
from notion_client import Client

NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "")


def _client() -> Client:
    return Client(auth=NOTION_TOKEN)


def log_item(
    title: str,
    publication: str,
    url: str,
    summary: str,
    published: datetime | None,
    item_type: str,  # "Podcast" | "Newsletter"
) -> None:
    """Append a row to the Notion digest database."""
    if not NOTION_TOKEN or not NOTION_DATABASE_ID:
        print("[WARN] Notion credentials not configured — skipping log.")
        return

    date_str = (published or datetime.now(timezone.utc)).strftime("%Y-%m-%d")

    _client().pages.create(
        parent={"database_id": NOTION_DATABASE_ID},
        properties={
            "Title": {"title": [{"text": {"content": title}}]},
            "Publication": {"rich_text": [{"text": {"content": publication}}]},
            "URL": {"url": url or None},
            "Summary": {"rich_text": [{"text": {"content": summary[:2000]}}]},
            "Date": {"date": {"start": date_str}},
            "Type": {"select": {"name": item_type}},
        },
    )


def create_database_template() -> None:
    """
    Print the Notion database schema JSON that you can import via the API.
    Run once to understand what properties to create in your Notion DB.
    """
    schema = {
        "Title": {"title": {}},
        "Publication": {"rich_text": {}},
        "URL": {"url": {}},
        "Summary": {"rich_text": {}},
        "Date": {"date": {}},
        "Type": {"select": {"options": [{"name": "Podcast"}, {"name": "Newsletter"}]}},
    }
    import json
    print(json.dumps(schema, indent=2))


if __name__ == "__main__":
    create_database_template()

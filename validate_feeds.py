#!/usr/bin/env python3
"""
Validate that all configured RSS feeds are reachable and return valid XML.
Run this once to confirm setup: python validate_feeds.py
"""
import sys
import requests
import feedparser
from config.feeds import ALL_FEEDS

TIMEOUT = 15


def validate_feed(feed: dict) -> dict:
    name = feed["name"]
    url = feed["rss_url"]
    result = {"name": name, "url": url, "ok": False, "entries": 0, "error": None}

    try:
        resp = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "PodcastDigest/1.0"})
        resp.raise_for_status()
    except requests.RequestException as e:
        result["error"] = str(e)
        return result

    parsed = feedparser.parse(resp.text)
    if parsed.bozo and not parsed.entries:
        result["error"] = f"Feed parse error: {parsed.bozo_exception}"
        return result

    result["ok"] = True
    result["entries"] = len(parsed.entries)
    if parsed.entries:
        result["latest"] = parsed.entries[0].get("title", "—")
    return result


def main():
    print("\n=== RSS Feed Validation ===\n")
    all_ok = True
    for feed in ALL_FEEDS:
        r = validate_feed(feed)
        status = "✅" if r["ok"] else "❌"
        print(f"{status}  {r['name']}")
        print(f"   URL     : {r['url']}")
        if r["ok"]:
            print(f"   Entries : {r['entries']}")
            if "latest" in r:
                print(f"   Latest  : {r['latest']}")
        else:
            print(f"   ERROR   : {r['error']}")
            all_ok = False
        print()

    if not all_ok:
        print("⚠️  One or more feeds failed. Check config/feeds.py and update URLs.")
        sys.exit(1)
    else:
        print("All feeds are active and valid.")


if __name__ == "__main__":
    main()

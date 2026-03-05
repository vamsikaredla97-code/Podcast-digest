"""
Transcript fetching via Supadata API and Spotify/YouTube link lookup.

Supadata API docs: https://supadata.ai/documentation/youtube/get-transcript
Auth: x-api-key header
"""
import re
import os
import requests

SUPADATA_API_KEY = os.getenv("SUPADATA_API_KEY", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")

_SUPADATA_BASE = "https://api.supadata.ai/v1"


# ── YouTube helpers ────────────────────────────────────────────────────────────

def _extract_video_id(url: str) -> str | None:
    patterns = [
        r"youtu\.be/([A-Za-z0-9_-]{11})",
        r"youtube\.com/watch\?.*v=([A-Za-z0-9_-]{11})",
        r"youtube\.com/embed/([A-Za-z0-9_-]{11})",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None


def search_youtube(query: str) -> str | None:
    """Return the URL of the top YouTube result for query, or None."""
    if not YOUTUBE_API_KEY:
        return None
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": 1,
        "key": YOUTUBE_API_KEY,
    }
    try:
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params=params,
            timeout=10,
        )
        r.raise_for_status()
        items = r.json().get("items", [])
        if items:
            vid_id = items[0]["id"]["videoId"]
            return f"https://www.youtube.com/watch?v={vid_id}"
    except Exception as e:
        print(f"[WARN] YouTube search failed: {e}")
    return None


def get_transcript(youtube_url: str) -> str | None:
    """
    Fetch the full transcript for a YouTube video using the Supadata API.
    Returns the concatenated transcript text, or None on failure.
    """
    if not SUPADATA_API_KEY:
        print("[WARN] SUPADATA_API_KEY not set — skipping transcript fetch.")
        return None

    video_id = _extract_video_id(youtube_url)
    if not video_id:
        print(f"[WARN] Could not extract video ID from: {youtube_url}")
        return None

    try:
        r = requests.get(
            f"{_SUPADATA_BASE}/youtube/transcript",
            params={"videoId": video_id, "text": "true"},
            headers={"x-api-key": SUPADATA_API_KEY},
            timeout=30,
        )
        if r.status_code == 404:
            print(f"[WARN] No transcript available for video {video_id}")
            return None
        r.raise_for_status()
        data = r.json()
        # Response: {"content": [{"text": "...", "offset": 0, "duration": 5000}], ...}
        # When text=true, content may be a plain string instead.
        content = data.get("content", "")
        if isinstance(content, str):
            return content.strip() or None
        if isinstance(content, list):
            return " ".join(seg.get("text", "") for seg in content).strip() or None
    except Exception as e:
        print(f"[WARN] Supadata transcript fetch failed for {video_id}: {e}")
    return None


# ── Spotify helpers ────────────────────────────────────────────────────────────

_spotify_token: str | None = None


def _get_spotify_token() -> str | None:
    global _spotify_token
    if _spotify_token:
        return _spotify_token
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        return None
    try:
        r = requests.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "client_credentials"},
            auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET),
            timeout=10,
        )
        r.raise_for_status()
        _spotify_token = r.json()["access_token"]
        return _spotify_token
    except Exception as e:
        print(f"[WARN] Spotify auth failed: {e}")
        return None


def search_spotify(podcast_name: str, episode_title: str) -> str | None:
    """Return Spotify URL for an episode, or None."""
    token = _get_spotify_token()
    if not token:
        return None
    query = f"{podcast_name} {episode_title}"
    try:
        r = requests.get(
            "https://api.spotify.com/v1/search",
            params={"q": query, "type": "episode", "limit": 1},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        r.raise_for_status()
        items = r.json().get("episodes", {}).get("items", [])
        if items:
            return items[0]["external_urls"]["spotify"]
    except Exception as e:
        print(f"[WARN] Spotify search failed: {e}")
    return None

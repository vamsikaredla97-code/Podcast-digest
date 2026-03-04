"""
YouTube transcript fetching and Spotify link lookup.
"""
import re
import os
import requests
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")


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
    Return the full transcript text for a YouTube video, or None on failure.
    """
    video_id = _extract_video_id(youtube_url)
    if not video_id:
        return None
    try:
        segments = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join(s["text"] for s in segments)
    except (NoTranscriptFound, TranscriptsDisabled) as e:
        print(f"[WARN] No transcript for {video_id}: {e}")
        return None
    except Exception as e:
        print(f"[WARN] Transcript fetch failed for {video_id}: {e}")
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

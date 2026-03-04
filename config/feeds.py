"""
RSS feed configuration for all podcast and newsletter sources.

Feed URLs researched and cross-referenced via Apple Podcasts, Podnews,
Podchaser, Feedspot, and Substack in March 2026.

IMPORTANT: Libsyn, Substack, and Stratechery all return HTTP 403 to headless
fetchers (anti-scraping). This is normal — feeds are valid and active in RSS
readers. The feed_checker.py sets a browser-like User-Agent to work around this.

Run `python validate_feeds.py` after initial setup to confirm all feeds respond.
"""

PODCAST_FEEDS = [
    {
        "name": "The Twenty Minute VC",
        "short_name": "20VC",
        # Hosted on Libsyn. Apple Podcasts ID: 958230465
        # Spotify: https://open.spotify.com/show/3j2KMcZTtgTNBKwtZBMHvl
        "rss_url": "https://thetwentyminutevc.libsyn.com/rss",
        "spotify_show_url": "https://open.spotify.com/show/3j2KMcZTtgTNBKwtZBMHvl",
        "type": "podcast",
        "emoji": "🎙️",
    },
    {
        "name": "Lenny's Podcast",
        "short_name": "Lenny's Podcast",
        # Hosted on Substack (publication ID: 10845). Audio is free; transcripts paywalled.
        # Apple Podcasts ID: 1627920305
        # Spotify: https://open.spotify.com/show/2dR1MUZEHCOnz1LVfNac0j
        "rss_url": "https://api.substack.com/feed/podcast/10845.rss",
        "spotify_show_url": "https://open.spotify.com/show/2dR1MUZEHCOnz1LVfNac0j",
        "type": "podcast",
        "emoji": "🎙️",
    },
    {
        "name": "All-In Podcast",
        "short_name": "All-In",
        # Hosted on Libsyn (Chamath, Jason, Sacks, Friedberg). Apple Podcasts ID: 1502871393
        # Spotify: https://open.spotify.com/show/2IqXAVFR4e0Bmyjsdc8QzF
        "rss_url": "https://allinchamathjason.libsyn.com/rss",
        "spotify_show_url": "https://open.spotify.com/show/2IqXAVFR4e0Bmyjsdc8QzF",
        "type": "podcast",
        "emoji": "🎙️",
    },
]

NEWSLETTER_FEEDS = [
    {
        "name": "Not Boring",
        "short_name": "Not Boring",
        "author": "Packy McCormick",
        # Substack with custom domain. Both URLs resolve to the same content.
        # Paid "Not Boring World" tier launched Jan 2026.
        "rss_url": "https://www.notboring.co/feed",
        "rss_url_alt": "https://notboring.substack.com/feed",
        "type": "newsletter",
        "emoji": "📝",
    },
    {
        "name": "The Generalist",
        "short_name": "The Generalist",
        "author": "Mario Gabriele",
        # Substack with custom domain. Articles mostly free; community paywalled.
        "rss_url": "https://www.generalist.com/feed",
        "rss_url_alt": "https://generalist.substack.com/feed",
        "type": "newsletter",
        "emoji": "📝",
    },
]

ALL_FEEDS = PODCAST_FEEDS + NEWSLETTER_FEEDS

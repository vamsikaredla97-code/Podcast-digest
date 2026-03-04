"""
RSS feed configuration for all podcast and newsletter sources.

Feed URLs sourced and cross-referenced via Apple Podcasts, Substack, Libsyn,
and Megaphone in March 2026. Run `python validate_feeds.py` to confirm all
feeds are live before first use.
"""

PODCAST_FEEDS = [
    {
        "name": "The Twenty Minute VC",
        "short_name": "20VC",
        # Distributed via Megaphone (Harry Stebbings / The Twentyminutevc Fund)
        # Apple Podcasts ID: 958230465
        "rss_url": "https://feeds.megaphone.fm/twentyminutevc",
        "type": "podcast",
        "emoji": "🎙️",
    },
    {
        "name": "Lenny's Podcast",
        "short_name": "Lenny's Podcast",
        # Distributed via Simplecast; hosted at lennysnewsletter.com
        # Apple Podcasts ID: 1627920305
        "rss_url": "https://www.lennysnewsletter.com/podcast/feed",
        "rss_url_alt": "https://feeds.simplecast.com/OKKkUFPr",
        "type": "podcast",
        "emoji": "🎙️",
    },
    {
        "name": "All-In Podcast",
        "short_name": "All-In",
        # Distributed via Libsyn (Chamath, Jason, Sacks, Friedberg)
        # Apple Podcasts ID: 1502871393
        "rss_url": "https://allinchamathjason.libsyn.com/rss",
        "type": "podcast",
        "emoji": "🎙️",
    },
]

NEWSLETTER_FEEDS = [
    {
        "name": "Stratechery",
        "short_name": "Stratechery",
        "author": "Ben Thompson",
        # Free public feed — member-only posts appear truncated
        "rss_url": "https://stratechery.com/feed",
        "type": "newsletter",
        "emoji": "📝",
        "note": "Free articles only; member-only posts are paywalled",
    },
    {
        "name": "Not Boring",
        "short_name": "Not Boring",
        "author": "Packy McCormick",
        # Packy McCormick's Substack
        "rss_url": "https://notboring.substack.com/feed",
        "type": "newsletter",
        "emoji": "📝",
    },
    {
        "name": "The Generalist",
        "short_name": "The Generalist",
        "author": "Mario Gabriele",
        # Mario Gabriele's newsletter at generalist.com
        "rss_url": "https://www.generalist.com/feed",
        "type": "newsletter",
        "emoji": "📝",
    },
]

ALL_FEEDS = PODCAST_FEEDS + NEWSLETTER_FEEDS

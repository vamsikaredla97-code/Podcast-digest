"""
RSS feed configuration for all podcast and newsletter sources.

Feed URLs researched and cross-referenced via Apple Podcasts, Podnews,
Podchaser, Feedspot, and Substack in March 2026.

IMPORTANT: Libsyn and some Substack feeds return HTTP 403 to headless
fetchers (anti-scraping). This is normal — feeds are valid and active in RSS
readers. feed_checker.py sets a browser-like User-Agent to work around this.

To add your own feeds, append a dict to PODCAST_FEEDS or NEWSLETTER_FEEDS
following the same schema. Run `python validate_feeds.py` to confirm they work.
"""

PODCAST_FEEDS = [
    {
        "name": "The Twenty Minute VC",
        "short_name": "20VC",
        # Hosted on Libsyn. Apple Podcasts ID: 958230465
        "rss_url": "https://thetwentyminutevc.libsyn.com/rss",
        "spotify_show_url": "https://open.spotify.com/show/3j2KMcZTtgTNBKwtZBMHvl",
        "type": "podcast",
    },
    {
        "name": "Lenny's Podcast",
        "short_name": "Lenny's Podcast",
        # Hosted on Substack. Apple Podcasts ID: 1627920305
        "rss_url": "https://api.substack.com/feed/podcast/10845.rss",
        "spotify_show_url": "https://open.spotify.com/show/2dR1MUZEHCOnz1LVfNac0j",
        "type": "podcast",
    },
    {
        "name": "All-In Podcast",
        "short_name": "All-In",
        # Chamath, Jason, Sacks, Friedberg. Apple Podcasts ID: 1502871393
        "rss_url": "https://allinchamathjason.libsyn.com/rss",
        "spotify_show_url": "https://open.spotify.com/show/2IqXAVFR4e0Bmyjsdc8QzF",
        "type": "podcast",
    },
    {
        "name": "Acquired",
        "short_name": "Acquired",
        # Ben Gilbert & David Rosenthal — long-form company histories.
        # Apple Podcasts ID: 1050462261
        "rss_url": "https://acquired.fm/rss",
        "spotify_show_url": "https://open.spotify.com/show/7Fj0XEuUQLUqoMZQdsLXqp",
        "type": "podcast",
    },
    {
        "name": "My First Million",
        "short_name": "MFM",
        # Sam Parr & Shaan Puri. Apple Podcasts ID: 1469759170
        "rss_url": "https://feeds.megaphone.fm/HS2300184645",
        "spotify_show_url": "https://open.spotify.com/show/0fgECiMqqVjVLiDivMiPsE",
        "type": "podcast",
    },
    {
        "name": "Lex Fridman Podcast",
        "short_name": "Lex Fridman",
        # Apple Podcasts ID: 1434243584
        "rss_url": "https://lexfridman.com/feed/podcast/",
        "spotify_show_url": "https://open.spotify.com/show/2MAi0BvDc6GTFvKFPXnkCL",
        "type": "podcast",
    },
    {
        "name": "How I Built This",
        "short_name": "How I Built This",
        # Guy Raz / NPR. Apple Podcasts ID: 1150510297
        "rss_url": "https://feeds.npr.org/510313/podcast.xml",
        "spotify_show_url": "https://open.spotify.com/show/6E709HRH7XaiZrMfgtNCun",
        "type": "podcast",
    },
]

NEWSLETTER_FEEDS = [
    {
        "name": "Not Boring",
        "short_name": "Not Boring",
        "author": "Packy McCormick",
        # Substack with custom domain.
        "rss_url": "https://www.notboring.co/feed",
        "rss_url_alt": "https://notboring.substack.com/feed",
        "type": "newsletter",
    },
    {
        "name": "The Generalist",
        "short_name": "The Generalist",
        "author": "Mario Gabriele",
        # Substack with custom domain.
        "rss_url": "https://www.generalist.com/feed",
        "rss_url_alt": "https://generalist.substack.com/feed",
        "type": "newsletter",
    },
    {
        "name": "Morning Brew",
        "short_name": "Morning Brew",
        "author": "Morning Brew",
        "rss_url": "https://www.morningbrew.com/daily/feed.rss",
        "type": "newsletter",
    },
    {
        "name": "The Hustle",
        "short_name": "The Hustle",
        "author": "The Hustle",
        "rss_url": "https://thehustle.co/feed/",
        "type": "newsletter",
    },
    {
        "name": "TLDR Newsletter",
        "short_name": "TLDR",
        "author": "TLDR",
        # Daily tech digest — startups, science, programming.
        "rss_url": "https://tldr.tech/rss/tech",
        "type": "newsletter",
    },
    {
        "name": "Stratechery",
        "short_name": "Stratechery",
        "author": "Ben Thompson",
        # Free articles only (Daily Updates are paywalled).
        # Returns 403 to bots — feed_checker User-Agent spoofing handles this.
        "rss_url": "https://stratechery.com/feed/",
        "type": "newsletter",
    },
]

ALL_FEEDS = PODCAST_FEEDS + NEWSLETTER_FEEDS

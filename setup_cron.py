#!/usr/bin/env python3
"""
Install the daily 07:00 cron job for the digest.

Usage:
    python setup_cron.py install   — add cron entry
    python setup_cron.py remove    — remove cron entry
    python setup_cron.py show      — print current crontab
"""
import sys
import os
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
PYTHON = sys.executable
DIGEST_SCRIPT = SCRIPT_DIR / "digest.py"
LOG_FILE = SCRIPT_DIR / "digest.log"
CRON_MARKER = "# podcast-newsletter-digest"


def get_crontab() -> str:
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else ""


def set_crontab(content: str) -> None:
    proc = subprocess.run(["crontab", "-"], input=content, text=True, capture_output=True)
    if proc.returncode != 0:
        print(f"[ERROR] crontab set failed: {proc.stderr}")
        sys.exit(1)


def install() -> None:
    current = get_crontab()
    if CRON_MARKER in current:
        print("Cron job already installed.")
        return

    timezone = os.getenv("TIMEZONE", "America/New_York")
    # Use TZ env var in the cron entry so the 07:00 is in the user's timezone
    cron_line = (
        f"0 7 * * * TZ={timezone} {PYTHON} {DIGEST_SCRIPT} >> {LOG_FILE} 2>&1 {CRON_MARKER}\n"
    )
    new_crontab = current.rstrip("\n") + "\n" + cron_line
    set_crontab(new_crontab)
    print(f"✅ Cron job installed: runs daily at 07:00 {timezone}")
    print(f"   Log: {LOG_FILE}")


def remove() -> None:
    current = get_crontab()
    lines = [l for l in current.splitlines(keepends=True) if CRON_MARKER not in l]
    set_crontab("".join(lines))
    print("✅ Cron job removed.")


def show() -> None:
    crontab = get_crontab()
    print(crontab or "(empty crontab)")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "install"
    if cmd == "install":
        install()
    elif cmd == "remove":
        remove()
    elif cmd == "show":
        show()
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python setup_cron.py [install|remove|show]")
        sys.exit(1)

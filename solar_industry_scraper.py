"""
solar_industry_scraper.py
─────────────────────────
Scrapes NewsAPI every hour for headlines containing
“utility scale solar” and appends them to a CSV.

• Compatible with Python 3.7+
• Works even if NEWSAPI_KEY isn’t set (uses FALLBACK_KEY below)
"""

import os
import time
import urllib3
import requests
import pandas as pd
from typing import List, Dict
from datetime import datetime, timezone
import schedule                    # pip install schedule

# ─────────────────── CONFIG ───────────────────
SEARCH_TERM = "utility scale solar"
CSV_PATH    = "utility_scale_solar_news.csv"
PAGE_SIZE   = 50                   # ≤ 100 for NewsAPI

# 1) Preferred: read key from env
API_KEY = os.getenv("NEWSAPI_KEY")

# 2) Fallback: paste your key here ONLY for quick tests
FALLBACK_KEY = "65f5a4def63d49ad841fa06abb2b4798"
if not API_KEY and FALLBACK_KEY:
    API_KEY = FALLBACK_KEY
# ──────────────────────────────────────────────

# Disable SSL warnings ONLY because we’re passing verify=False below.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def fetch_utility_scale_solar_news(api_key: str) -> List[Dict]:
    """Return a cleaned list of article dictionaries from NewsAPI."""
    url = (
        "https://newsapi.org/v2/everything"
        f"?q={SEARCH_TERM.replace(' ', '%20')}"
        "&language=en"
        "&sortBy=publishedAt"
        f"&pageSize={PAGE_SIZE}"
        f"&apiKey={api_key}"
    )

    try:
        # verify=False is a *temporary* workaround for your SSL chain issue
        r = requests.get(url, timeout=15, verify=False)
        r.raise_for_status()
    except requests.RequestException as err:
        print("🔴 Request error:", err)
        return []

    cleaned: List[Dict] = [
        {
            "date_scraped": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "published_at": a.get("publishedAt", ""),
            "title":        a.get("title", ""),
            "source":       a.get("source", {}).get("name", ""),
            "url":          a.get("url", ""),
        }
        for a in r.json().get("articles", [])
    ]
    return cleaned


def update_csv() -> None:
    """Fetch fresh news and append new, deduplicated rows to the CSV."""
    if not API_KEY:
        print("❌ No NewsAPI key found. Set NEWSAPI_KEY or edit FALLBACK_KEY.")
        return

    print(f"⏰ Scraping at {datetime.now(timezone.utc).isoformat(timespec='seconds')} …")
    fresh_rows = fetch_utility_scale_solar_news(API_KEY)
    if not fresh_rows:
        return

    new_df = pd.DataFrame(fresh_rows)

    if os.path.exists(CSV_PATH):
        combined = (
            pd.concat([pd.read_csv(CSV_PATH), new_df], ignore_index=True)
              .drop_duplicates(subset="url")
              .sort_values("published_at", ascending=False)
        )
    else:
        combined = new_df

    combined.to_csv(CSV_PATH, index=False)
    print(f"✅ Added {len(new_df)} new rows • Total rows: {len(combined)}")


if __name__ == "__main__":
    update_csv()                    # run once at start-up
    schedule.every().hour.do(update_csv)

    print("🟢 Scraper running every hour (Ctrl-C to exit).")
    while True:
        schedule.run_pending()
        time.sleep(30)






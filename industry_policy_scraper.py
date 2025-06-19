"""
industry_policy_scraper.py
──────────────────────────
Scrapes NewsAPI every hour for headlines on solar / renewable-energy
policy changes in Canada, the U.S., and Australia, and appends them
to policy_news.csv

• Requires:  requests, pandas, schedule  (pip install …)
• Run once and leave running:  python industry_policy_scraper.py
"""

import os
import time
import schedule
import requests
import pandas as pd
from datetime import datetime
import urllib3

# ─── Disable SSL warnings (because we’re bypassing cert verification) ──────────
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ─── Config ────────────────────────────────────────────────────────────────────
API_KEY   = os.getenv("NEWSAPI_KEY") or "YOUR_FALLBACK_KEY"
CSV_PATH  = "policy_news.csv"

QUERY     = "solar OR renewable"
POLICIES  = "policy OR regulation OR bill OR law"
COUNTRIES = ["ca", "us", "au"]       # NewsAPI country codes
PAGE_SIZE = 100                      # ≤100

# ─── Scraper function ──────────────────────────────────────────────────────────
def scrape():
    rows = []
    for c in COUNTRIES:
        url = (
            "https://newsapi.org/v2/top-headlines?"
            f"apiKey={API_KEY}"
            f"&q=({QUERY}) AND ({POLICIES})"
            f"&language=en&pageSize={PAGE_SIZE}&country={c}"
        )
        try:
            # NOTE: verify=False bypasses SSL cert validation ★
            response = requests.get(url, timeout=15, verify=False)
            data = response.json()
        except Exception as e:
            print(f"[{datetime.utcnow()}] ❌ Request error for {c.upper()}: {e}")
            continue

        for art in data.get("articles", []):
            rows.append({
                "Date Scraped": datetime.utcnow(),
                "Country"     : c.upper(),
                "Title"       : art["title"],
                "Source"      : art["source"]["name"],
                "Link"        : art["url"],
            })

    if not rows:
        print(f"[{datetime.utcnow()}] No new policy articles found.")
        return

    df_new = pd.DataFrame(rows)
    if os.path.isfile(CSV_PATH):
        df_old = pd.read_csv(CSV_PATH)
        df_new = (
            pd.concat([df_old, df_new], ignore_index=True)
              .drop_duplicates("Link")
              .reset_index(drop=True)
        )
    df_new.to_csv(CSV_PATH, index=False)
    print(f"[{datetime.utcnow()}] ✅ {len(rows)} policy headlines saved.")

# ─── Main loop ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    scrape()                         # run immediately at launch
    schedule.every().hour.do(scrape)

    print("⏳ Policy scraper running … will scrape every hour.")
    while True:
        schedule.run_pending()
        time.sleep(60)


"""
competitor_solar_news_scraper.py
────────────────────────────────
Scrapes NewsAPI every hour for solar-related headlines that
mention any competitor in the list below and appends them to
competitor_solar_news.csv.

• Requires: requests, pandas, schedule  ➜  pip install -U requests pandas schedule
• Run once and leave running:  python competitor_solar_news_scraper.py
"""

import os, time, schedule, requests, pandas as pd
from datetime import datetime, timezone
import urllib3; urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_KEY  = os.getenv("NEWSAPI_KEY") or "YOUR_FALLBACK_KEY"
CSV_PATH = "competitor_solar_news.csv"
PAGE_SZ  = 100       # NewsAPI max = 100

COMPANIES = [
    "Grupo Ortiz", "NoBull Energy", "WHC", "Webber", "Moss", "Primoris", "SOLV Energy",
    "Quanta Services", "Black & Veatch", "Kiewit", "McCarthy", "Mortensen", "RES",
    "Q CELLS", "Borea Construction", "GRS Energy", "Bechtel", "GP Joule",
    "Goldbeck Solar", "LPL Solar", "DEP COM Power", "Alltrade", "Rosendin",
    "Beon Energy", "UGL", "Bouygues", "Acciona", "DT Infrastructure",
    "Ferrovial", "Green Grid Connect", "Enerven", "RJE Global", "CPP",
    "TEC-C", "Decmil", "Wolff Power", "BMD Group"
]

SOLAR_TERMS = "(solar OR photovoltaic OR PV)"

def scrape():
    rows = []
    for company in COMPANIES:
        q = f'"{company}" AND {SOLAR_TERMS}'
        url = (
            "https://newsapi.org/v2/everything?"
            f"apiKey={API_KEY}&q={requests.utils.quote(q)}"
            f"&language=en&pageSize={PAGE_SZ}&sortBy=publishedAt"
        )
        try:
            data = requests.get(url, timeout=15, verify=False).json()
        except Exception as e:
            print(f"[{company}] request error ➜ {e}")
            continue

        for art in data.get("articles", []):
            rows.append({
                "Date Scraped": datetime.now(timezone.utc),
                "Company"     : company,
                "Title"       : art["title"],
                "Source"      : art["source"]["name"],
                "Link"        : art["url"],
            })

    if not rows:
        print(f"[{datetime.now(timezone.utc)}] No new company solar headlines.")
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
    print(f"[{datetime.now(timezone.utc)}] ✅ {len(rows)} solar headlines added.")

if __name__ == "__main__":
    scrape()
    schedule.every().hour.do(scrape)
    print("⏳ Competitor solar-news scraper running …")
    while True:
        schedule.run_pending()
        time.sleep(60)

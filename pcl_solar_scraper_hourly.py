import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import urllib3
import schedule
import time

# Disable SSL warnings (needed for Renew Canada)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Keywords to match only "PCL Solar" mentions
keywords = ["pcl solar"]

# Sources to scrape
sources = [
    {
        "name": "ConstructConnect",
        "url": "https://canada.constructconnect.com/search?q=pcl%20solar",
        "base": "https://canada.constructconnect.com"
    },
    {
        "name": "Renew Canada",
        "url": "https://www.renewcanada.net/?s=pcl+solar",
        "base": "https://www.renewcanada.net"
    },
    {
        "name": "DCN",
        "url": "https://canada.constructconnect.com/dcn/search?q=pcl%20solar",
        "base": "https://canada.constructconnect.com"
    }
]

def run_scraper():
    print(f"\n Scraper running at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    results = []

    for site in sources:
        print(f"\nScraping {site['name']}...")
        try:
            verify_ssl = site["name"] != "Renew Canada"
            response = requests.get(site["url"], headers={"User-Agent": "Mozilla/5.0"}, verify=verify_ssl)
            soup = BeautifulSoup(response.text, "html.parser")

            for link in soup.find_all("a", href=True):
                title = link.get_text(strip=True)
                href = link["href"]
                full_url = href if href.startswith("http") else site["base"] + href

                if any(k in title.lower() for k in keywords):
                    results.append({
                        "Source": site["name"],
                        "Title": title,
                        "Link": full_url,
                        "Date Scraped": datetime.today().strftime("%Y-%m-%d")
                    })
                    print(f"{title}")

        except Exception as e:
            print(f"Failed to scrape {site['name']}: {e}")

    if results:
        df_new = pd.DataFrame(results)

        try:
            df_existing = pd.read_csv("PCL_solar_news.csv")
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            df_combined.drop_duplicates(subset=["Title", "Link"], inplace=True)
        except FileNotFoundError:
            df_combined = df_new

        df_combined.to_csv("PCL_solar_news.csv", index=False)
        print(f"\n Saved {len(df_combined)} unique articles to 'PCL_solar_news.csv'")
    else:
        print("No new matching articles found this run.")

# Run once on startup
run_scraper()

# 🔁 Schedule to run every hour
schedule.every(1).hours.do(run_scraper)

# Loop to keep the scheduler running
while True:
    schedule.run_pending()
    time.sleep(60)




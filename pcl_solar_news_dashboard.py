import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import schedule
import urllib3

# Disable SSL warnings (for Renew Canada)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Target keywords (strict filter)
keywords = ["pcl solar", "pcl construction"]

# Define news sources to scrape
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

def scrape_articles():
    results = []

    for source in sources:
        print(f"🔍 Scraping {source['name']}...")
        try:
            response = requests.get(source["url"], headers={"User-Agent": "Mozilla/5.0"}, verify=False, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            for result in soup.select(".dbsr, .search-result, article"):
                title_tag = result.select_one("div[role='heading'], h3, h2, .search-title")
                link_tag = result.select_one("a[href]")
                snippet_tag = result.select_one("div:not([role='heading']), p, .search-snippet")

                if title_tag and link_tag:
                    title = title_tag.get_text(strip=True)
                    link = link_tag['href']
                    snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""

                    text = f"{title.lower()} {snippet.lower()}"
                    if any(keyword in text for keyword in keywords):
                        results.append({
                            "Query": "PCL Solar",
                            "Title": title,
                            "Source": source["name"],
                            "Link": link if link.startswith("http") else source["base"] + link,
                            "Snippet": snippet,
                            "Date Scraped": datetime.utcnow().isoformat()
                        })

        except Exception as e:
            print(f"❌ Failed to scrape {source['name']}: {e}")

    if results:
        df = pd.DataFrame(results)
        df.to_csv("PCL_solar_news.csv", index=False)
        print(f"✅ Done! Saved {len(df)} filtered articles to 'PCL_solar_news.csv'\n")
    else:
        print("⚠️ No relevant articles found.\n")

# Run once immediately
scrape_articles()

# Schedule to run hourly
schedule.every(1).hours.do(scrape_articles)

while True:
    schedule.run_pending()
    time.sleep(60)





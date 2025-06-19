import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import urllib3

# Disable SSL warnings (needed for RenewCanada)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Keywords to match in titles
keywords = ["pcl", "pcl construction", "pcl solar"]

# Sites to scrape
sources = [
    {
        "name": "ConstructConnect",
        "url": "https://canada.constructconnect.com/search?q=pcl",
        "base": "https://canada.constructconnect.com"
    },
    {
        "name": "Renew Canada",
        "url": "https://www.renewcanada.net/?s=pcl",
        "base": "https://www.renewcanada.net"
    },
    {
        "name": "DCN",
        "url": "https://canada.constructconnect.com/dcn/search?q=pcl",
        "base": "https://canada.constructconnect.com"
    }
]

results = []

# Loop through each site
for site in sources:
    print(f"\n🔍 Scraping {site['name']}...")

    try:
        # Disable SSL only for Renew Canada
        verify_ssl = site["name"] != "Renew Canada"
        response = requests.get(site["url"], headers={"User-Agent": "Mozilla/5.0"}, verify=verify_ssl)
        soup = BeautifulSoup(response.text, "html.parser")

        # Scan all links for relevant titles
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
                print(f"✅ {title}")

    except Exception as e:
        print(f"❌ Failed to scrape {site['name']}: {e}")

# Save results to CSV
df = pd.DataFrame(results)
df.to_csv("PCL_industry_news.csv", index=False)
print(f"\n✅ Done! Saved {len(results)} filtered articles to 'PCL_industry_news.csv'")


import socket
import ssl
import json
import pandas as pd
from datetime import datetime

API_KEY = "65f5a4def63d49ad841fa06abb2b4798"  # 🔑 Replace with your real NewsAPI key

# Define high-relevance search queries
queries = [
    '"PCL Construction" OR "PCL Constructors"',
    '"PCL Solar Canada"',
    '"PCL Solar USA"',
    '"PCL Solar Australia"'
]

# Only accept articles with these exact phrases in the title
required_title_keywords = [
    "pcl construction",
    "pcl constructors",
    "pcl solar canada",
    "pcl solar usa",
    "pcl solar australia"
]

results = []

for query in queries:
    print(f"\n🔍 Searching for: {query}")
    context = ssl._create_unverified_context()

    try:
        with socket.create_connection(("newsapi.org", 443)) as sock:
            with context.wrap_socket(sock, server_hostname="newsapi.org") as ssock:
                encoded_query = query.replace(" ", "%20").replace('"', '%22').replace("OR", "%20OR%20")
                path = f"/v2/everything?q={encoded_query}&pageSize=10&language=en&sortBy=publishedAt"
                request = f"GET {path} HTTP/1.1\r\n" \
                          f"Host: newsapi.org\r\n" \
                          f"User-Agent: PythonSocket\r\n" \
                          f"X-Api-Key: {API_KEY}\r\n" \
                          f"Connection: close\r\n\r\n"
                ssock.send(request.encode())

                response = b""
                while True:
                    data = ssock.recv(4096)
                    if not data:
                        break
                    response += data

        # Parse body
        body = response.split(b"\r\n\r\n", 1)[1]
        parsed = json.loads(body)

        for article in parsed.get("articles", []):
            title = (article.get("title") or "").lower()
            snippet = (article.get("description") or "").lower()

            # ✅ Only keep articles with an exact keyword match in the title
            if not any(phrase in title for phrase in required_title_keywords):
                continue

            results.append({
                "Query": query.replace('%22', '"'),
                "Title": article.get("title", ""),
                "Source": article["source"]["name"],
                "Published At": article["publishedAt"],
                "Link": article["url"],
                "Snippet": article.get("description", "")
            })

            print(f"✅ {article['title']}")

    except Exception as e:
        print(f"❌ Error during search for '{query}': {e}")

# Save results
df = pd.DataFrame(results)
df.to_csv("PCL_solar_news.csv", index=False)
print(f"\n✅ Done! Saved {len(results)} filtered articles to 'PCL_solar_news.csv'")






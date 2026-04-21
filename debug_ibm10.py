import httpx
import re

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}

with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    r = client.get("https://www.ibm.com/marketplace/static/components/search/insights/ibm-search-insights.js")
    js = r.text

# Find where the search fetch actually happens - look around 'fetch(' calls
for m in re.finditer(r'fetch\(', js):
    start = max(0, m.start()-300)
    end = min(len(js), m.start()+300)
    snippet = js[start:end]
    if any(k in snippet.lower() for k in ['ibm', 'search', 'api', 'career', 'url', 'host']):
        print("=== fetch context ===")
        print(snippet)
        print()

# Find URL building with template literals or concatenation around 'search'
for m in re.finditer(r'search', js, re.IGNORECASE):
    start = max(0, m.start()-100)
    end = min(len(js), m.start()+200)
    snippet = js[start:end]
    if 'ibm.com' in snippet or 'apiUrl' in snippet or 'endpoint' in snippet.lower():
        print("=== search URL context ===")
        print(snippet[:300])
        print()

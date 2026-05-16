import httpx
import re

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}

with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    r = client.get("https://www.ibm.com/marketplace/static/components/search/insights/ibm-search-insights.js")
    js = r.text

with open("ibm_search.js", "w", encoding="utf-8") as f:
    f.write(js)

# Search for all strings between quotes that look like API paths or domains
# Specifically look for something like /search or /api in the context of careers
print("=== Strings containing 'search' ===")
hits = re.findall(r'["\']([^"\'\n]{0,20}search[^"\'\n]{0,50})["\']', js, re.IGNORECASE)
for h in list(dict.fromkeys(hits))[:40]:
    print(h)

print()
print("=== Strings containing 'career' ===")
hits2 = re.findall(r'["\']([^"\'\n]{0,20}career[^"\'\n]{0,80})["\']', js, re.IGNORECASE)
for h in list(dict.fromkeys(hits2))[:20]:
    print(h)

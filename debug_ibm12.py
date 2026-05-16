import httpx
import re

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}

with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    r = client.get("https://www.ibm.com/marketplace/static/components/search/insights/ibm-search-insights.js")
    js = r.text

# Save and search for any string containing "search" and dot notation (like .search? or /search?)
print("Length:", len(js))

# Find all occurrences of 'query' or 'rows' or 'offset' near a URL-like pattern
for kw in ["query", "rows", "offset", "facets", "filters", "appid", "scopeid"]:
    positions = [m.start() for m in re.finditer(kw, js, re.IGNORECASE)]
    for pos in positions[:3]:
        ctx = js[max(0,pos-200):pos+200]
        if any(c in ctx for c in ['http', 'url', 'fetch', 'axios', 'request']):
            print(f"=== '{kw}' near http/url ===")
            print(ctx)
            print()
            break

# Look for XMLHttpRequest usage
xhr_pos = js.find("XMLHttpRequest")
if xhr_pos > 0:
    print("=== XMLHttpRequest context ===")
    print(js[max(0,xhr_pos-100):xhr_pos+500])

# Look for axios or got patterns
for lib in ['axios', '.request(', 'got(', 'superagent']:
    pos = js.find(lib)
    if pos > 0:
        print(f"=== {lib} context ===")
        print(js[max(0,pos-100):pos+300])

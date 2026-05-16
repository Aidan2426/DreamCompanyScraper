import httpx
import re

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}

with httpx.Client(timeout=15, headers=HEADERS, follow_redirects=True) as client:
    r = client.get("https://www.ibm.com/marketplace/static/components/search/insights/ibm-search-insights.js")
    js = r.text

# Find base URL strings
hits = re.findall(r'"(https?://[^"]{10,100})"', js)
print("=== HTTPS URLs in JS ===")
for h in list(dict.fromkeys(hits))[:30]:
    print(h)

print()
print("=== Path patterns with query params ===")
hits2 = re.findall(r'"(/[a-zA-Z0-9/_\-]{5,60}\?[a-zA-Z]{2,}[^"]{0,60})"', js)
for h in list(dict.fromkeys(hits2))[:20]:
    print(h)

print()
print("=== Mentions of 'rows' or 'start' (pagination params) ===")
for m in re.finditer(r'.{50}(rows|start|offset|page).{50}', js):
    print(m.group())

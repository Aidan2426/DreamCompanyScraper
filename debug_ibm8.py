import httpx
import re
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
}

with open("debug_ibm.html", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")

# Get all JS chunk files loaded by Next.js
js_files = []
for script in soup.find_all("script", src=True):
    src = script["src"]
    if "_next" in src or "chunks" in src or "static" in src:
        if src.startswith("/"):
            src = "https://www.ibm.com" + src
        js_files.append(src)

print(f"Next.js chunks: {len(js_files)}")
for f in js_files:
    print(" ", f[:100])

print()
# Fetch and search each chunk for careers API
with httpx.Client(timeout=15, headers=HEADERS, follow_redirects=True) as client:
    for js_url in js_files:
        try:
            r = client.get(js_url)
            js = r.text
            # Look for API patterns
            hits = []
            for pattern in [r'careers["\s/][^"<]{3,80}', r'api[Uu]rl["\s:]+["\'][^"\']{5,80}', r'baseURL["\s:]+["\'][^"\']{5,80}', r'endpoint["\s:]+["\'][^"\']{5,80}']:
                found = re.findall(pattern, js)
                hits.extend(found)
            if hits:
                print(f"=== {js_url[-50:]} ===")
                for h in list(dict.fromkeys(hits))[:10]:
                    print(" ", h[:120])
        except Exception as e:
            print(f"ERR {js_url[-40:]}: {e}")

import httpx
import re
import json
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
}

with open("debug_ibm.html", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")

# Check for __NEXT_DATA__
next_data = soup.find("script", id="__NEXT_DATA__")
if next_data:
    print("Found __NEXT_DATA__")
    data = json.loads(next_data.get_text())
    print(json.dumps(data, indent=2)[:2000])
else:
    print("No __NEXT_DATA__")

# Check pageProps script more carefully
for script in soup.find_all("script", type="application/json"):
    txt = script.get_text()
    if "pageProps" in txt:
        try:
            data = json.loads(txt)
            print("pageProps JSON:")
            print(json.dumps(data, indent=2)[:3000])
        except:
            print("Raw:", txt[:500])

# Look for React hydration data or initial state
for pattern in [r'window\.__INITIAL_STATE__\s*=\s*({.+?});', r'__APP_PROPS__\s*=\s*({.+?})', r'initialData\s*=\s*({.+?});']:
    m = re.search(pattern, html, re.DOTALL)
    if m:
        print(f"Found {pattern[:20]}: {m.group(1)[:500]}")

# Look for API base URL in all scripts
print("\n=== All script content search for API patterns ===")
for script in soup.find_all("script"):
    txt = script.get_text()
    if any(k in txt for k in ["apiUrl", "apiBase", "baseUrl", "endpoint", "host"]) and len(txt) < 3000:
        print("Script snippet:", txt[:600])
        print()

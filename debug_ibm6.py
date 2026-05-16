import httpx
import re
import json
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    # Look at the IBM careers search page more carefully
    r = client.get("https://www.ibm.com/careers/search?sort=dcdate_desc")
    soup = BeautifulSoup(r.text, "lxml")

    # Find all data-* attributes that might hint at API
    all_data_attrs = {}
    for tag in soup.find_all(True):
        for attr, val in tag.attrs.items():
            if attr.startswith("data-") and val:
                all_data_attrs[attr] = val

    print("=== data-* attributes ===")
    for k, v in all_data_attrs.items():
        print(f"  {k}: {str(v)[:100]}")

    print()
    # Find JSON-LD or embedded JSON
    for script in soup.find_all("script"):
        t = script.get("type", "")
        txt = script.get_text()
        if "application/json" in t or "application/ld+json" in t:
            print(f"JSON script ({t}):", txt[:300])

    print()
    # Find window.* assignments
    for script in soup.find_all("script"):
        txt = script.get_text()
        if "window." in txt and len(txt) < 5000:
            print("window script:", txt[:500])
            print()

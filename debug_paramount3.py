import httpx
import re
import json
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://careers.paramount.com/search/",
    "X-Requested-With": "XMLHttpRequest",
}

BASE = "https://careers.paramount.com"

with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    # Seed session
    client.get(f"{BASE}/search/", headers={**HEADERS, "Accept": "text/html"})

    # Get first page of tiles
    r = client.get(f"{BASE}/search/tile-search-results/",
                   params={"q": "", "sortColumn": "referencedate", "sortDirection": "desc", "startrow": 0})
    body = r.text
    print(f"Response size: {len(body)}")

    # Check if there's total count info
    total_match = re.search(r'(\d+)\s*(?:jobs?|results?|positions?)', body, re.IGNORECASE)
    if total_match:
        print(f"Total hint: {total_match.group(0)}")

    # Parse with BeautifulSoup
    soup = BeautifulSoup(body, "html.parser")

    # Find all job tiles
    tiles = soup.find_all("li", class_=re.compile(r"job-tile"))
    print(f"\nJob tiles found: {len(tiles)}")

    if tiles:
        # Inspect first tile fully
        t = tiles[0]
        print(f"\nFirst tile HTML:")
        print(t.prettify()[:2000])

    # Check the full response for total count
    print("\n=== Full response text (first 3000) ===")
    print(body[:3000])

    # Check for pagination info
    print("\n=== Last 1000 chars ===")
    print(body[-1000:])

    # Test with startrow=25
    print("\n=== Page 2 (startrow=25) ===")
    r2 = client.get(f"{BASE}/search/tile-search-results/",
                    params={"q": "", "sortColumn": "referencedate", "sortDirection": "desc", "startrow": 25})
    body2 = r2.text
    soup2 = BeautifulSoup(body2, "html.parser")
    tiles2 = soup2.find_all("li", class_=re.compile(r"job-tile"))
    print(f"Tiles on page 2: {len(tiles2)}")
    if tiles2:
        print("First tile data-url:", tiles2[0].get("data-url"))

    # Check main search page for total count
    print("\n=== Main page total count ===")
    r3 = client.get(f"{BASE}/search/",
                    params={"q": "", "sortColumn": "referencedate", "sortDirection": "desc"},
                    headers={**HEADERS, "Accept": "text/html"})
    total_hits = re.findall(r'(\d[\d,]*)\s*(?:job|result|position)', r3.text, re.IGNORECASE)
    print("Total count mentions:", total_hits[:10])

    # Check if response has total in a data attribute or comment
    total_in_resp = re.findall(r'total["\s:=]+(\d+)', body, re.IGNORECASE)
    print("Total in tile response:", total_in_resp[:5])

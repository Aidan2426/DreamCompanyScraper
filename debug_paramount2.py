import httpx
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://careers.paramount.com/search/",
}

BASE = "https://careers.paramount.com"

with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    # Seed cookies
    r0 = client.get(f"{BASE}/search/", params={"q": "", "sortColumn": "referencedate", "sortDirection": "desc"})
    print("Cookies:", list(client.cookies.keys()))

    # Try tile-search-results endpoint
    print("\n=== tile-search-results tests ===")
    tile_urls = [
        f"{BASE}/search/tile-search-results/",
        f"{BASE}/tile-search-results/",
        f"{BASE}/search/tile-search-results",
        f"{BASE}/tile-search-results",
    ]
    for url in tile_urls:
        params = {"q": "", "sortColumn": "referencedate", "sortDirection": "desc", "startrow": 0, "rk": 0}
        r = client.get(url, params=params)
        ct = r.headers.get("content-type", "")
        print(f"\n{url}")
        print(f"  Status: {r.status_code}, CT: {ct[:60]}")
        if r.status_code == 200:
            if "json" in ct:
                d = r.json()
                print(f"  Keys: {list(d.keys()) if isinstance(d, dict) else type(d)}")
                print(f"  Preview: {json.dumps(d)[:500]}")
            else:
                print(f"  Body (500): {r.text[:500]}")

    # Also check the JS file for exact API call pattern
    print("\n=== Scanning searchResults JS ===")
    r_js = client.get(f"{BASE}/platform/js/j2w/min/j2w.searchResults.min.js?h=47df3f59",
                      headers={**HEADERS, "Accept": "*/*"})
    js = r_js.text
    print(f"JS size: {len(js)}")

    # Find URL patterns
    urls = re.findall(r'["\`]([^"\`]{5,100}tile[^"\`]{0,60})["\`]', js)
    print("tile refs:")
    for u in sorted(set(urls))[:10]:
        print(" ", u)

    # Find ajax/fetch calls
    ajax = re.findall(r'\.(?:get|post|ajax)\s*\(\s*["\`]([^"\`]{5,100})["\`]', js)
    print("\najax calls:")
    for a in sorted(set(ajax))[:15]:
        print(" ", a)

    # Find any URL parameter patterns
    params_pat = re.findall(r'startrow|rk=|sortColumn|pageNo|start=', js)
    print("\nParam keywords found:", sorted(set(params_pat)))

    # Find all string URLs
    all_urls = re.findall(r'"(/[^"]{3,80})"', js)
    print("\nAll path strings:")
    for u in sorted(set(all_urls))[:20]:
        print(" ", u)

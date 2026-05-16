import httpx
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,*/*",
    "Accept-Language": "en-US,en;q=0.9",
}

BASE = "https://nps.usajobs.gov"

with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    r = client.get(f"{BASE}/search/results/",
                   params={"a": "IN10", "s": "startdate", "sd": "desc", "p": 1})
    print(f"Status: {r.status_code}, CT: {r.headers.get('content-type','')}, size: {len(r.text)}")
    body = r.text

    # Look for embedded JSON / job data
    if "__NEXT_DATA__" in body:
        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', body, re.DOTALL)
        if m:
            nd = json.loads(m.group(1))
            print("__NEXT_DATA__ keys:", list(nd.keys()))

    # Look for job data in scripts
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', body, re.DOTALL)
    for i, s in enumerate(scripts):
        if len(s) > 200 and any(x in s for x in ['"jobs"', '"SearchResult"', '"PositionTitle"', '"totalJobs"', 'window.__']):
            print(f"\nScript {i} ({len(s)} chars):")
            print(s[:800])

    # API refs
    api_refs = re.findall(r'["\']((?:https?://[^"\']*|/[^"\']*)?(?:api|search|jobs)[^"\']{0,80})["\']', body)
    print("\nAPI refs:")
    for a in sorted(set(api_refs))[:20]:
        print(" ", a)

    # Check for job count
    counts = re.findall(r'(\d+)\s*(?:job|result|position)', body, re.IGNORECASE)
    print(f"\nCount mentions: {counts[:10]}")

    # Try JSON endpoint
    print("\n=== JSON endpoint tests ===")
    for url in [
        f"{BASE}/search/results/?a=IN10&s=startdate&sd=desc&p=1&format=json",
        f"{BASE}/api/search?a=IN10&s=startdate&sd=desc&p=1",
        "https://nps.usajobs.gov/api/search/results?AgencyCode=IN10",
        "https://www.usajobs.gov/Search/Results?a=IN10&s=startdate&sd=desc&p=1",
    ]:
        r2 = client.get(url, headers={**HEADERS, "Accept": "application/json, */*"})
        ct = r2.headers.get("content-type", "")
        print(f"\n{url[:80]}: {r2.status_code}, CT={ct[:50]}")
        if "json" in ct and r2.status_code == 200:
            d = r2.json()
            print("Keys:", list(d.keys()) if isinstance(d, dict) else type(d))

    print("\n=== Body start ===")
    print(body[:3000])

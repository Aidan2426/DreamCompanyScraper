import httpx
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://careers.adobe.com/us/en/search-results",
}

BASE = "https://careers.adobe.com"

with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    print("=== GET page ===")
    r = client.get(f"{BASE}/us/en/search-results")
    print(f"Status: {r.status_code}, CT: {r.headers.get('content-type','')}")
    body = r.text
    print(f"Page size: {len(body)}")
    print("Cookies:", list(client.cookies.keys()))

    # Look for __NEXT_DATA__ or similar
    if "__NEXT_DATA__" in body:
        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', body, re.DOTALL)
        if m:
            nd = json.loads(m.group(1))
            print("__NEXT_DATA__ keys:", list(nd.keys()))
            pp = nd.get("props", {}).get("pageProps", {})
            print("pageProps keys:", list(pp.keys()))

    # API refs in HTML
    api_refs = re.findall(r'["\']((?:https?://[^"\']*|/[^"\']*)?(?:api|search|jobs)[^"\']{0,80})["\']', body)
    print("\nAPI refs:")
    for a in sorted(set(api_refs))[:20]:
        print(" ", a)

    # Script tags with job data
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', body, re.DOTALL)
    for i, s in enumerate(scripts):
        if len(s) > 100 and any(x in s.lower() for x in ['"jobs"', '"results"', '"postings"', 'apiurl', 'endpoint']):
            print(f"\nScript {i}: {s[:500]}")

    # Common Phenom/AEM/custom patterns
    print("\n=== API tests ===")
    candidates = [
        f"{BASE}/api/jobs?country=us&language=en&start=0&num=10",
        f"{BASE}/us/en/search-results.json?start=0&num=10",
        f"{BASE}/api/jobs/search?country=us&start=0&num=10",
        f"{BASE}/us/en/api/jobs?start=0&num=10",
        f"https://www.adobe.com/careers/search.json?q=&start=0&num=10",
        f"{BASE}/api/search?q=&country=us&start=0&num=10",
        f"https://adobejobs.adobe.com/api/jobs?start=0&num=10",
    ]
    for url in candidates:
        try:
            r2 = client.get(url)
            ct = r2.headers.get("content-type", "")
            print(f"\n{url}")
            print(f"  Status: {r2.status_code}, CT: {ct[:60]}")
            if r2.status_code == 200 and "json" in ct:
                d = r2.json()
                print(f"  Keys: {list(d.keys()) if isinstance(d, dict) else type(d)}")
                print(f"  Preview: {json.dumps(d)[:300]}")
        except Exception as e:
            print(f"  Error: {e}")

    print("\n=== Body start ===")
    print(body[:3000])

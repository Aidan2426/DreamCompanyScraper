import httpx
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://micron.eightfold.ai/careers",
}

BASE = "https://micron.eightfold.ai"

with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    # Try common Eightfold API patterns
    print("=== Testing Eightfold API patterns ===")
    candidates = [
        f"{BASE}/api/apply/v3/jobs?domain=micron.com&start=0&num=10&sort_by=timestamp",
        f"{BASE}/api/apply/v2/jobs?domain=micron.com&start=0&num=10",
        f"{BASE}/api/jobs?start=0&num=10&sort_by=timestamp",
        f"{BASE}/careers/api/jobs?start=0&num=10&sort_by=timestamp",
        f"{BASE}/api/apply/v1/jobs?domain=micron&start=0&num=10",
        f"{BASE}/api/apply/v3/jobs?domain=micron&start=0&num=10&sort_by=timestamp",
        # With pid from URL
        f"{BASE}/api/apply/v3/jobs?pid=38899809&start=0&num=10",
        f"{BASE}/api/apply/v3/jobs?start=0&num=10&sort_by=timestamp&pid=38899809",
    ]
    for url in candidates:
        try:
            r = client.get(url)
            ct = r.headers.get("content-type", "")
            print(f"\n{url}")
            print(f"  Status: {r.status_code}, CT: {ct[:60]}")
            if r.status_code == 200 and "json" in ct:
                d = r.json()
                print(f"  Keys: {list(d.keys()) if isinstance(d, dict) else type(d)}")
                print(f"  Preview: {json.dumps(d)[:300]}")
        except Exception as e:
            print(f"  Error: {e}")

    # Also fetch the page to look for embedded data or API hints
    print("\n=== GET careers page ===")
    r2 = client.get(f"{BASE}/careers", params={"start": 0, "sort_by": "timestamp"})
    print(f"Status: {r2.status_code}, CT: {r2.headers.get('content-type','')}")
    body = r2.text

    # Look for API URLs in page source
    api_refs = re.findall(r'["\']((?:https?://[^"\']*|/[^"\']*)?(?:api|graphql|jobs)[^"\']{0,100})["\']', body)
    print("API refs found:")
    for a in sorted(set(api_refs))[:20]:
        print(" ", a)

    # Look for __NEXT_DATA__ or similar
    if "__NEXT_DATA__" in body:
        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', body, re.DOTALL)
        if m:
            nd = json.loads(m.group(1))
            print("\n__NEXT_DATA__ keys:", list(nd.keys()))

    # Look for window.__data or similar
    data_vars = re.findall(r'window\.(\w+)\s*=\s*(\{.*?\});', body[:5000], re.DOTALL)
    for var, val in data_vars[:5]:
        print(f"\nwindow.{var}:", val[:200])

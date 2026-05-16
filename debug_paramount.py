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
    # Fetch page to find structure
    print("=== GET search page ===")
    r = client.get(f"{BASE}/search/", params={
        "createNewAlert": "false", "q": "", "locationsearch": "",
        "optionsFacetsDD_customfield1": "", "optionsFacetsDD_customfield2": "", "optionsFacetsDD_customfield3": ""
    })
    print(f"Status: {r.status_code}, CT: {r.headers.get('content-type','')}")
    body = r.text
    print(f"Page size: {len(body)}")
    print("Cookies:", list(client.cookies.keys()))

    # Look for embedded JSON / job data
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', body, re.DOTALL)
    print(f"\nScript tags: {len(scripts)}")
    for i, s in enumerate(scripts):
        if len(s) > 50 and any(x in s.lower() for x in ['job', 'position', 'posting', 'requisition']):
            print(f"\nScript {i} (len={len(s)}):")
            print(s[:600])

    # Find API refs
    api_refs = re.findall(r'["\']((?:/|https?://)[^"\']{5,100}(?:api|search|jobs|requisition)[^"\']{0,60})["\']', body)
    print("\nAPI refs:")
    for a in sorted(set(api_refs))[:20]:
        print(" ", a)

    # Look for __NEXT_DATA__ or similar
    for marker in ['__NEXT_DATA__', 'window.__data', 'window.__STATE', 'initialData']:
        if marker in body:
            idx = body.find(marker)
            print(f"\n{marker} found at {idx}:")
            print(body[idx:idx+500])

    # Check body start for structure hints
    print("\n=== Body start ===")
    print(body[:3000])

    # Try common Phenom/Taleo/Workday patterns
    print("\n=== API endpoint tests ===")
    test_urls = [
        f"{BASE}/api/jobs?start=0&num=10",
        f"{BASE}/search/api/jobs?q=&start=0&num=10",
        f"{BASE}/api/search?q=&start=0&num=10",
        f"{BASE}/jobs/search?format=json&q=&start=0",
        f"https://phf.tbe.taleo.net/phf04/ats/careers/v2/searchResults?org=PARAMOUNT&cws=37",
        f"{BASE}/search/?createNewAlert=false&q=&format=json",
    ]
    for url in test_urls:
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

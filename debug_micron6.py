import httpx
import re
import json

HEADERS_BASE = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

BASE = "https://micron.eightfold.ai"

with httpx.Client(timeout=30, headers=HEADERS_BASE, follow_redirects=True) as client:
    # Load page to get cookies + CSRF
    r0 = client.get(f"{BASE}/careers", params={"start": 0, "sort_by": "timestamp"},
                    headers={**HEADERS_BASE, "Accept": "text/html"})
    csrf = re.search(r'name="_csrf"\s+content="([^"]+)"', r0.text)
    csrf_token = csrf.group(1) if csrf else ""
    print(f"CSRF token: {csrf_token[:30]}...")
    print(f"Cookies: {dict(client.cookies)}")

    api_headers = {
        **HEADERS_BASE,
        "Accept": "application/json",
        "X-CSRFToken": csrf_token,
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"{BASE}/careers?start=0&sort_by=timestamp",
        "Content-Type": "application/json",
    }

    # Try pcsx/search endpoint
    print("\n=== /api/pcsx/search ===")
    for params in [
        {"domain": "micron.eightfold.ai", "start": 0, "num": 10, "sort_by": "timestamp"},
        {"domain": "micron.com", "start": 0, "num": 10, "sort_by": "timestamp"},
        {"domain": "micron.eightfold.ai", "start": 0, "num": 10},
        {"start": 0, "num": 10, "sort_by": "timestamp"},
    ]:
        r = client.get(f"{BASE}/api/pcsx/search", params=params, headers=api_headers)
        ct = r.headers.get("content-type", "")
        print(f"\nparams={list(params.keys())} domain={params.get('domain','none')}: {r.status_code}, CT={ct[:50]}")
        if r.status_code == 200 and "json" in ct:
            d = r.json()
            print(f"  Keys: {list(d.keys()) if isinstance(d, dict) else type(d)}")
            print(f"  Preview: {json.dumps(d)[:500]}")
        elif r.status_code != 403:
            print(f"  Body: {r.text[:300]}")

    # Also try the apply/v2/search which is common in eightfold
    print("\n=== Other search patterns ===")
    for path in [
        "/api/apply/v2/positions/search",
        "/api/positions?start=0&num=10&sort_by=timestamp&domain=micron.com",
        "/api/apply/v2/positions?start=0&num=10",
        "/careers?start=0&num=10&sort_by=timestamp&format=json",
    ]:
        r2 = client.get(f"{BASE}{path}", headers={**api_headers, "Accept": "application/json"})
        ct2 = r2.headers.get("content-type", "")
        print(f"\n{path}: {r2.status_code}, CT={ct2[:50]}")
        if "json" in ct2 and r2.status_code == 200:
            d = r2.json()
            print(f"  Keys: {list(d.keys()) if isinstance(d, dict) else type(d)}")

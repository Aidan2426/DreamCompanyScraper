import httpx
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Referer": "https://micron.eightfold.ai/careers",
}

BASE = "https://micron.eightfold.ai"

with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    # Load page to get cookies + JS list
    r0 = client.get(f"{BASE}/careers", params={"start": 0, "sort_by": "timestamp"})

    scripts = re.findall(r'src=["\'](/gen/js/[^"\']+)["\']', r0.text)
    print(f"Found {len(scripts)} JS files")

    # Search main app JS for API patterns
    api_hits = []
    for s in scripts[:15]:
        url = f"{BASE}{s}"
        try:
            r = client.get(url)
            if r.status_code != 200:
                continue
            content = r.text
            # Find API path patterns
            hits = re.findall(r'["\`](/(?:api|careers)[^"\`\s]{3,80})["\`]', content)
            hits += re.findall(r'url\s*:\s*["\`]([^"\`]{10,80})["\`]', content)
            if hits:
                print(f"\n{s}:")
                for h in sorted(set(hits))[:15]:
                    print(f"  {h}")
                api_hits.extend(hits)
        except Exception as e:
            print(f"Error {s}: {e}")

    # Check if page has embedded job JSON in script tags
    job_data = re.findall(r'var\s+\w*[Jj]ob\w*\s*=\s*(\[.*?\]);', r0.text, re.DOTALL)
    for d in job_data[:3]:
        print("\nJob var:", d[:300])

    # Look at entire HTML for any JSON that contains job-like structures
    # Search for "title" + "location" patterns
    if '"title"' in r0.text and '"location"' in r0.text:
        # Try to find job list JSON
        blobs = re.findall(r'\{[^{}]{0,50}"title"[^{}]{0,200}"location"[^{}]{0,200}\}', r0.text)
        print(f"\nJob-like blobs in HTML: {len(blobs)}")
        for b in blobs[:2]:
            print(b[:300])

    # Try the careers endpoint with JSON accept header and XMLHttpRequest
    print("\n=== Trying careers JSON requests ===")
    for params in [
        {"start": 0, "num": 10, "sort_by": "timestamp"},
        {"start": 0, "num": 10, "sort_by": "timestamp", "pid": "38899809"},
    ]:
        r2 = client.get(f"{BASE}/careers", params=params,
                        headers={**HEADERS,
                                 "Accept": "application/json",
                                 "X-Requested-With": "XMLHttpRequest"})
        ct = r2.headers.get("content-type", "")
        print(f"\nparams={list(params.keys())}: {r2.status_code}, CT={ct[:50]}")
        if "json" in ct:
            d = r2.json()
            print("Keys:", list(d.keys()) if isinstance(d, dict) else type(d))
            print("Preview:", json.dumps(d)[:400])

    # Try /careers/search or similar
    print("\n=== Additional endpoint tests ===")
    for path in ["/careers/search", "/careers/jobs", "/search/jobs", "/api/search"]:
        r3 = client.get(f"{BASE}{path}",
                        params={"start": 0, "num": 10, "sort_by": "timestamp"},
                        headers={**HEADERS, "Accept": "application/json"})
        print(f"{path}: {r3.status_code}, CT={r3.headers.get('content-type','')[:40]}")
        if r3.status_code == 200 and "json" in r3.headers.get("content-type", ""):
            print(" Keys:", list(r3.json().keys()))

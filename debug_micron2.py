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
    # Seed cookies from main page
    r0 = client.get(f"{BASE}/careers", params={"start": 0, "sort_by": "timestamp"})
    print("Cookies after page load:", list(client.cookies.keys()))
    print("Cookies values:", dict(client.cookies))

    # Find JS bundle
    scripts = re.findall(r'src=["\']([^"\']+\.js[^"\']*)["\']', r0.text)
    print("\nScripts:", scripts[:10])

    # Look for chunk manifests
    chunks = re.findall(r'["\']([^"\']*chunk[^"\']*\.js)["\']', r0.text)
    print("Chunks:", chunks[:5])

    # Try v2 with cookies set
    print("\n=== v2 with cookies ===")
    r = client.get(f"{BASE}/api/apply/v2/jobs",
                   params={"domain": "micron.com", "start": 0, "num": 10, "sort_by": "timestamp"},
                   headers={**HEADERS, "X-Requested-With": "XMLHttpRequest"})
    print(f"Status: {r.status_code}, CT: {r.headers.get('content-type','')}")
    print("Body:", r.text[:500])

    # Try with domain=micron.eightfold.ai
    r2 = client.get(f"{BASE}/api/apply/v2/jobs",
                    params={"domain": "micron.eightfold.ai", "start": 0, "num": 10, "sort_by": "timestamp"})
    print(f"\nWith domain=micron.eightfold.ai: {r2.status_code}")
    print("Body:", r2.text[:300])

    # Try POST
    r3 = client.post(f"{BASE}/api/apply/v2/jobs",
                     json={"domain": "micron.com", "start": 0, "num": 10, "sort_by": "timestamp"})
    print(f"\nPOST v2: {r3.status_code}")

    # Try graphql
    r4 = client.post(f"{BASE}/graphql",
                     json={"query": "{ jobs { title } }"})
    print(f"\nGraphQL: {r4.status_code}")

    # Inspect the HTML for any embedded job data
    body = r0.text
    # Look for JSON blobs
    json_blobs = re.findall(r'window\.__(?:INITIAL|STATE|DATA|REDUX)__\s*=\s*({.*?});', body, re.DOTALL)
    for blob in json_blobs[:3]:
        print("\nWindow data:", blob[:400])

    # Look for script tags with JSON
    script_jsons = re.findall(r'<script[^>]*type=["\']application/json["\'][^>]*>(.*?)</script>', body, re.DOTALL)
    for sj in script_jsons[:3]:
        print("\nScript JSON:", sj[:400])

    # Look for any fetch/XHR patterns
    api_patterns = re.findall(r'["\'](/api/[^"\'?\s]{3,60})["\']', body)
    print("\nAPI patterns in HTML:", list(set(api_patterns))[:20])

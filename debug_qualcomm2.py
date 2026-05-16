import httpx
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Referer": "https://apply.appcast.io/l/qualcomm-careers-us",
}

BASE = "https://apply.appcast.io"

with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    # Get HTML to find JS bundle URLs
    r = client.get(f"{BASE}/l/qualcomm-careers-us", params={"__ssr": "true"})
    html = r.text

    # Find all script src
    scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html)
    print("Scripts found:")
    for s in scripts:
        print(" ", s)

    # Find JS chunks
    chunks = re.findall(r'["\'](/l/[^"\']+\.js)["\']', html)
    print("\nJS chunks:")
    for c in chunks[:10]:
        print(" ", c)

    # Try to find API URL patterns in the main bundle
    # Look for "api" references in HTML
    api_refs = re.findall(r'["\']([^"\']*api[^"\']*)["\']', html)
    print("\nAPI refs in HTML:")
    for a in set(api_refs[:20]):
        print(" ", a)

    # Try fetching one of the main JS files if found
    main_js_urls = [s for s in scripts if 'main' in s.lower() or 'chunk' in s.lower()]
    print(f"\nMain JS candidates: {main_js_urls[:5]}")

    # Try common Appcast API patterns
    print("\n=== Testing API patterns ===")
    test_urls = [
        f"{BASE}/api/1/jobs?placement_slug=qualcomm-careers-us&page=1&per_page=12",
        f"{BASE}/api/1/placements/qualcomm-careers-us/jobs?page=1&per_page=12",
        f"{BASE}/api/placements/qualcomm-careers-us/jobs?page=1",
        f"{BASE}/api/v2/jobs?placement_slug=qualcomm-careers-us&page=1",
        f"{BASE}/api/1/placements/qualcomm-careers-us",
        f"{BASE}/placements/qualcomm-careers-us/jobs.json?page=1",
    ]
    for url in test_urls:
        try:
            r2 = client.get(url, headers={**HEADERS, "Accept": "application/json"})
            ct = r2.headers.get("content-type", "")
            print(f"\n{url}")
            print(f"  Status: {r2.status_code}, CT: {ct[:60]}")
            if r2.status_code == 200:
                if "json" in ct:
                    d = r2.json()
                    print(f"  Keys: {list(d.keys()) if isinstance(d, dict) else type(d)}")
                else:
                    print(f"  Body (500): {r2.text[:500]}")
        except Exception as e:
            print(f"  Error: {e}")

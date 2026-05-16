import httpx
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,*/*",
    "Accept-Language": "en-US,en;q=0.9",
}

BASE = "https://micron.eightfold.ai"

with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    # Get CSRF token from page
    r0 = client.get(f"{BASE}/careers", params={"start": 0, "sort_by": "timestamp"})
    csrf = re.search(r'name="_csrf"\s+content="([^"]+)"', r0.text)
    csrf_token = csrf.group(1) if csrf else ""
    print(f"CSRF: {csrf_token[:40]}...")
    print(f"Cookies: {dict(client.cookies)}")

    # Scan pcsxPwa JS for API patterns
    pwa_script = re.search(r'src="(/gen/js/pcsxPwa\.[^"]+)"', r0.text)
    if pwa_script:
        js_url = f"{BASE}{pwa_script.group(1)}"
        print(f"\nFetching: {js_url}")
        rjs = client.get(js_url, headers={**HEADERS, "Accept": "*/*"})
        js = rjs.text
        print(f"JS size: {len(js)} chars")

        # Find API path strings
        api_paths = re.findall(r'["\`](/api/[^"\`\s,;()]{3,100})["\`]', js)
        print(f"\nAPI paths in pcsxPwa:")
        for p in sorted(set(api_paths)):
            print(f"  {p}")

        # Find fetch/ajax call patterns
        fetch_patterns = re.findall(r'(?:fetch|ajax|get|post)\s*\(\s*["\`]([^"\`]{5,100})["\`]', js)
        print(f"\nFetch patterns:")
        for p in sorted(set(fetch_patterns))[:20]:
            print(f"  {p}")

        # Look for "positions" or "jobs" keywords near URL strings
        pos_context = re.findall(r'.{0,50}(?:position|jobs).{0,100}', js)
        for ctx in pos_context[:10]:
            print(f"\nContext: {ctx[:200]}")

    # Try v2 with CSRF header
    print("\n=== v2 with CSRF header ===")
    headers_with_csrf = {
        **HEADERS,
        "Accept": "application/json",
        "X-CSRFToken": csrf_token,
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"{BASE}/careers",
    }
    r2 = client.get(f"{BASE}/api/apply/v2/jobs",
                    params={"domain": "micron.com", "start": 0, "num": 10, "sort_by": "timestamp"},
                    headers=headers_with_csrf)
    print(f"Status: {r2.status_code}")
    print(f"Body: {r2.text[:500]}")

    # Try with X-CSRFToken directly from meta
    r3 = client.post(f"{BASE}/api/apply/v2/jobs",
                     json={"domain": "micron.com", "start": 0, "num": 10, "sort_by": "timestamp"},
                     headers=headers_with_csrf)
    print(f"\nPOST Status: {r3.status_code}")
    print(f"Body: {r3.text[:500]}")

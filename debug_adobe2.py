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
REF = "ADOBUS"

with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    client.get(f"{BASE}/us/en/search-results")

    print("=== Phenom widget API tests ===")
    widget_candidates = [
        f"{BASE}/widgets/jobs/search?refNum={REF}&country=us&language=en&from=0&num=10",
        f"{BASE}/widgets/jobs?refNum={REF}&from=0&num=10",
        f"{BASE}/widgets/{REF}/jobs?from=0&num=10",
        f"{BASE}/widgets/jobs/search?refNum={REF}&from=0&num=10&sort=date",
        f"{BASE}/widgets/jobs/search?refNum={REF}&from=0&num=10",
        f"{BASE}/widgets/job/search?refNum={REF}&country=us&from=0&num=10",
    ]
    for url in widget_candidates:
        try:
            r = client.get(url)
            ct = r.headers.get("content-type", "")
            print(f"\n{url}")
            print(f"  Status: {r.status_code}, CT: {ct[:60]}")
            if r.status_code == 200 and "json" in ct:
                d = r.json()
                print(f"  Keys: {list(d.keys()) if isinstance(d, dict) else type(d)}")
                print(f"  Preview: {json.dumps(d)[:400]}")
            elif r.status_code == 200:
                print(f"  Body: {r.text[:300]}")
        except Exception as e:
            print(f"  Error: {e}")

    # content-us Phenom API
    print("\n=== content-us Phenom API ===")
    content_candidates = [
        "https://content-us.phenompeople.com/api/content-delivery/caasContentV1?refNum=ADOBUS&country=us&language=en&from=0&num=10",
        "https://content-us.phenompeople.com/api/content-delivery/caasContentV1?refNum=ADOBUS&from=0&num=10",
    ]
    for url in content_candidates:
        try:
            r = client.get(url)
            ct = r.headers.get("content-type", "")
            print(f"\n{url[:80]}")
            print(f"  Status: {r.status_code}, CT: {ct[:60]}")
            if "json" in ct:
                d = r.json()
                print(f"  Keys: {list(d.keys()) if isinstance(d, dict) else type(d)}")
                print(f"  Preview: {json.dumps(d)[:300]}")
        except Exception as e:
            print(f"  Error: {e}")

    # Check ?from=10&s=1 pagination pattern from HTML
    print("\n=== Pagination URL pattern ===")
    r_p2 = client.get(f"{BASE}/us/en/search-results", params={"from": 10, "s": 1},
                      headers={**HEADERS, "Accept": "text/html"})
    print(f"Status: {r_p2.status_code}, size: {len(r_p2.text)}")

    # Scan main page JS for API calls
    r_main = client.get(f"{BASE}/us/en/search-results", headers={**HEADERS, "Accept": "text/html"})
    body = r_main.text

    # Find job data in page
    # Look for embedded JSON with jobs
    job_blobs = re.findall(r'"(?:jobs|results|jobList|postings)"\s*:\s*\[', body)
    print(f"\nJob array markers in HTML: {len(job_blobs)}")

    # Find all script src
    js_srcs = re.findall(r'src=["\']([^"\']+\.js[^"\']*)["\']', body)
    print(f"\nJS files: {len(js_srcs)}")
    # Find main/app JS
    main_js = [s for s in js_srcs if any(x in s for x in ['search', 'app', 'main', 'chunk', 'phenomtrack'])]
    print("Relevant JS:", main_js[:5])

    # Look for API endpoint in page scripts inline
    api_in_scripts = re.findall(r'(?:apiUrl|endpoint|api_url|searchUrl)\s*[=:]\s*["\']([^"\']{10,100})["\']', body)
    print("\nAPI in scripts:", api_in_scripts[:10])

    # Look for fetch or axios calls
    fetches = re.findall(r'(?:fetch|axios\.get|\.ajax)\(["\']([^"\']{10,100})["\']', body)
    print("Fetch calls:", fetches[:10])

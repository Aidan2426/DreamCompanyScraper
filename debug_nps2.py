import httpx
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "*/*",
}

with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    # Get the main JS
    r_js = client.get("https://nps.usajobs.gov/js/searchmain.js?v=o5FlVLKFvMKo1l0jzGRuBQI1YMIvZrP8Mt2FojJERSc")
    js = r_js.text
    print(f"JS size: {len(js)}")

    # Find API endpoints
    api_paths = re.findall(r'["\`](/(?:api|search|data)[^"\`\s]{3,100})["\`]', js)
    print("API paths:")
    for p in sorted(set(api_paths))[:20]:
        print(" ", p)

    # Find full URLs
    full_urls = re.findall(r'["\`](https?://[^"\`\s]{10,100})["\`]', js)
    print("\nFull URLs:")
    for u in sorted(set(full_urls))[:20]:
        print(" ", u)

    # Find fetch/axios calls
    fetches = re.findall(r'(?:fetch|axios)\s*\.\s*(?:get|post)\s*\(\s*["\`]([^"\`]{5,100})["\`]', js)
    print("\nFetch calls:")
    for f in sorted(set(fetches))[:15]:
        print(" ", f)

    # Find usajobs.gov specific patterns
    usajobs = re.findall(r'["\`]([^"\`]*usajobs[^"\`]{0,80})["\`]', js)
    print("\nUSAJobs refs:")
    for u in sorted(set(usajobs))[:15]:
        print(" ", u)

    # Look for Authorization or API key patterns
    auth = re.findall(r'["\`]([^"\`]*(?:Authorization|apikey|api.key|ApiKey)[^"\`]{0,80})["\`]', js, re.IGNORECASE)
    print("\nAuth patterns:")
    for a in auth[:10]:
        print(" ", a)

    # Find all string constants that look like API endpoints
    endpoints = re.findall(r'["\`](/[a-z][a-z0-9/._-]{5,60})["\`]', js)
    print("\nAll path strings:")
    for e in sorted(set(endpoints))[:20]:
        print(" ", e)

    # Try NPS-specific API patterns
    print("\n=== Testing NPS API endpoints ===")
    nps_base = "https://nps.usajobs.gov"
    for path in [
        "/api/search/results?a=IN10&p=1&s=startdate&sd=desc",
        "/Search/GetResults?a=IN10&p=1",
        "/api/jobs?a=IN10&p=1",
    ]:
        r2 = client.get(f"{nps_base}{path}", headers={**HEADERS, "Accept": "application/json"})
        ct = r2.headers.get("content-type", "")
        print(f"\n{path}: {r2.status_code}, CT={ct[:50]}")
        if "json" in ct:
            print("Keys:", list(r2.json().keys()) if isinstance(r2.json(), dict) else "array")

    # Try data.usajobs.gov without auth
    print("\n=== data.usajobs.gov without auth ===")
    r3 = client.get("https://data.usajobs.gov/api/search",
                    params={"AgencyCode": "IN10", "ResultsPerPage": 5, "Page": 1},
                    headers={**HEADERS, "Accept": "application/json"})
    print(f"Status: {r3.status_code}")
    print(f"Body: {r3.text[:200]}")

    # Try with email header (some USAJobs endpoints need email+key)
    r4 = client.get("https://data.usajobs.gov/api/search",
                    params={"AgencyCode": "IN10", "ResultsPerPage": 5, "Page": 1, "SortField": "OpenDate", "SortDirection": "Desc"},
                    headers={**HEADERS, "Accept": "application/json",
                             "User-Agent": "aash3@hawk.illinoistech.edu",
                             "Authorization-Key": "unused"})
    print(f"\nWith fake auth - Status: {r4.status_code}")
    print(f"Body: {r4.text[:200]}")

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
    r0 = client.get(f"{BASE}/us/en/search-results", headers={**HEADERS, "Accept": "text/html"})
    body = r0.text

    # Find the job array
    idx = body.find('"jobs"')
    if idx >= 0:
        print(f"'jobs' at {idx}:")
        print(body[idx:idx+2000])

    # Try content delivery with all required params
    print("\n=== content-us with full params ===")
    content_url = "https://content-us.phenompeople.com/api/content-delivery/caasContentV1"
    for params in [
        {"refNum": "ADOBUS", "siteType": "external", "locale": "en_us", "pageId": "page15"},
        {"refNum": "ADOBUS", "siteType": "external", "locale": "en_us", "pageId": "page15", "from": 0, "num": 10},
    ]:
        r = client.get(content_url, params=params)
        print(f"\nparams={list(params.keys())}: {r.status_code}")
        d = r.json()
        inner = d.get("caasContentV1", {})
        print(f"  status: {inner.get('status')}, errorMsg: {inner.get('errorMsg','')[:100]}")
        if inner.get("data"):
            print(f"  data keys: {list(inner['data'].keys()) if isinstance(inner['data'], dict) else type(inner['data'])}")
            print(f"  data: {json.dumps(inner['data'])[:500]}")

    # Look for the Phenom JS app config to find job search API
    print("\n=== Scan app-config JS ===")
    cfg_js_url = "https://cdn.phenompeople.com/CareerConnectResources/common/js/globalplatform/1773309038427_ph-app-config-5.0.js"
    r_js = client.get(cfg_js_url, headers={**HEADERS, "Accept": "*/*"})
    js = r_js.text
    print(f"JS size: {len(js)}")
    # Find API URLs
    api_paths = re.findall(r'["\`](/(?:api|jobs|search)[^"\`\s]{3,100})["\`]', js)
    print("API paths:")
    for p in sorted(set(api_paths))[:20]:
        print(" ", p)

    # Find all string assignments with 'search' or 'job'
    search_refs = re.findall(r'["\`]([^"\`]{10,100}(?:search|jobs?)[^"\`]{0,60})["\`]', js)
    print("\nSearch/job refs:")
    for s in sorted(set(search_refs))[:20]:
        print(" ", s)

    # Try the Phenom search API directly
    print("\n=== Phenom search API ===")
    for url in [
        "https://careers.adobe.com/api/jobs/search",
        "https://careers.adobe.com/api/jobs/searchresults",
        "https://careers.adobe.com/api/jobs/searchresults?refNum=ADOBUS&country=us&language=en&from=0&num=10",
        "https://phenom.svc.adobe.com/api/jobs?from=0&num=10",
    ]:
        try:
            r2 = client.get(url, params={"refNum": "ADOBUS", "country": "us", "language": "en", "from": 0, "num": 10} if "?" not in url else {})
            ct = r2.headers.get("content-type", "")
            print(f"\n{url}: {r2.status_code}, CT={ct[:50]}")
            if "json" in ct and r2.status_code == 200:
                d = r2.json()
                print(f"  Keys: {list(d.keys()) if isinstance(d, dict) else type(d)}")
                print(f"  Preview: {json.dumps(d)[:400]}")
            elif r2.status_code not in (404, 500):
                print(f"  Body: {r2.text[:300]}")
        except Exception as e:
            print(f"  Error: {e}")

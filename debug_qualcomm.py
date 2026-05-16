import httpx
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://apply.appcast.io/l/qualcomm-careers-us",
}

BASE = "https://apply.appcast.io"

with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    # First fetch the page to see structure and cookies
    print("=== GET landing page ===")
    r = client.get(f"{BASE}/l/qualcomm-careers-us", params={"__ssr": "true", "radius": "40miles"})
    print("Status:", r.status_code)
    print("Content-Type:", r.headers.get("content-type", ""))
    print("Cookies:", list(client.cookies.keys()))
    # Print first 3000 chars to find API hints
    body = r.text
    print("Body preview (3000 chars):")
    print(body[:3000])

    # Check for JSON embedded in HTML
    if "__NEXT_DATA__" in body:
        import re
        m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', body, re.DOTALL)
        if m:
            next_data = json.loads(m.group(1))
            print("\n=== __NEXT_DATA__ keys ===")
            print(list(next_data.keys()))
            props = next_data.get("props", {})
            print("props keys:", list(props.keys()))
            page_props = props.get("pageProps", {})
            print("pageProps keys:", list(page_props.keys()))
            # Look for jobs
            if "jobs" in page_props:
                jobs = page_props["jobs"]
                print(f"Jobs count: {len(jobs) if isinstance(jobs, list) else 'not list'}")
                if isinstance(jobs, list) and jobs:
                    print("First job keys:", list(jobs[0].keys()))
                    print("First job:", json.dumps(jobs[0], indent=2)[:500])
            # Dump full pageProps if small enough
            pp_str = json.dumps(page_props)
            if len(pp_str) < 5000:
                print("Full pageProps:", pp_str)
            else:
                print("pageProps (first 2000):", pp_str[:2000])

    # Try JSON API endpoint patterns
    print("\n=== Trying API endpoints ===")
    api_candidates = [
        f"{BASE}/api/jobs?slug=qualcomm-careers-us&page=1&per_page=12",
        f"{BASE}/api/v1/jobs?slug=qualcomm-careers-us&page=1",
        f"{BASE}/l/qualcomm-careers-us/jobs?page=1&per_page=12",
        f"{BASE}/api/feeds/qualcomm-careers-us?page=1",
    ]
    for url in api_candidates:
        try:
            r2 = client.get(url)
            print(f"\n{url}")
            print(f"  Status: {r2.status_code}, CT: {r2.headers.get('content-type','')[:60]}")
            if r2.status_code == 200 and "json" in r2.headers.get("content-type", ""):
                d = r2.json()
                print(f"  Keys: {list(d.keys()) if isinstance(d, dict) else type(d)}")
                print(f"  Preview: {json.dumps(d)[:300]}")
        except Exception as e:
            print(f"  Error: {e}")

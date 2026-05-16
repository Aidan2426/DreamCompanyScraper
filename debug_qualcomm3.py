import httpx
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://apply.appcast.io/l/qualcomm-careers-us",
}

BASE = "https://apply.appcast.io"
SLUG = "qualcomm-careers-us"

with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    # Check placement info
    print("=== Placement info ===")
    r = client.get(f"{BASE}/api/tools/landing_page/{SLUG}")
    print(f"Status: {r.status_code}, CT: {r.headers.get('content-type','')}")
    if r.status_code == 200:
        try:
            d = r.json()
            print("Keys:", list(d.keys()) if isinstance(d, dict) else type(d))
            print(json.dumps(d, indent=2)[:1000])
        except:
            print("Body:", r.text[:500])

    # Check jobs endpoint - no params
    print("\n=== Jobs endpoint (no params) ===")
    r2 = client.get(f"{BASE}/api/tools/landing_page/{SLUG}/jobs")
    print(f"Status: {r2.status_code}, CT: {r2.headers.get('content-type','')}")
    if r2.status_code == 200:
        try:
            d = r2.json()
            if isinstance(d, dict):
                print("Keys:", list(d.keys()))
                # Show meta/pagination info
                for k in ["total", "count", "per_page", "page", "pages", "meta", "pagination", "total_count"]:
                    if k in d:
                        print(f"  {k}: {d[k]}")
                # Show jobs preview
                for jobs_key in ["jobs", "results", "data", "items"]:
                    if jobs_key in d:
                        jobs = d[jobs_key]
                        print(f"  {jobs_key} count: {len(jobs)}")
                        if jobs:
                            print(f"  First job keys: {list(jobs[0].keys())}")
                            print(f"  First job: {json.dumps(jobs[0], indent=2)[:600]}")
                        break
            elif isinstance(d, list):
                print(f"Array of {len(d)} items")
                if d:
                    print("First item keys:", list(d[0].keys()))
                    print("First item:", json.dumps(d[0], indent=2)[:600])
        except Exception as e:
            print("Parse error:", e)
            print("Body:", r2.text[:500])

    # Try with pagination params
    print("\n=== Jobs with page params ===")
    for params in [
        {"page": 1, "per_page": 12},
        {"page": 1, "limit": 12},
        {"offset": 0, "limit": 12},
        {"p": 1},
    ]:
        r3 = client.get(f"{BASE}/api/tools/landing_page/{SLUG}/jobs", params=params)
        print(f"  params={params} -> {r3.status_code}, CT: {r3.headers.get('content-type','')[:50]}")
        if r3.status_code == 200 and "json" in r3.headers.get("content-type", ""):
            d = r3.json()
            if isinstance(d, dict):
                total_keys = [k for k in d if "total" in k.lower() or "count" in k.lower() or "page" in k.lower()]
                print(f"    Pagination keys: {total_keys}")
                print(f"    Keys: {list(d.keys())}")

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
    # Check page=1 with per_page=12
    r = client.get(f"{BASE}/api/tools/landing_page/{SLUG}/jobs", params={"page": 1, "per_page": 12})
    d = r.json()
    print("page=1, per_page=12:")
    print(f"  jobs_count: {d.get('jobs_count')}")
    print(f"  page: {d.get('page')}")
    print(f"  pages_total: {d.get('pages_total')}")
    print(f"  jobs returned: {len(d.get('jobs', []))}")

    # Check page=1 with per_page=25
    r2 = client.get(f"{BASE}/api/tools/landing_page/{SLUG}/jobs", params={"page": 1, "per_page": 25})
    d2 = r2.json()
    print("\npage=1, per_page=25:")
    print(f"  jobs_count: {d2.get('jobs_count')}")
    print(f"  page: {d2.get('page')}")
    print(f"  pages_total: {d2.get('pages_total')}")
    print(f"  jobs returned: {len(d2.get('jobs', []))}")

    # Check page=2
    r3 = client.get(f"{BASE}/api/tools/landing_page/{SLUG}/jobs", params={"page": 2, "per_page": 12})
    d3 = r3.json()
    print("\npage=2, per_page=12:")
    print(f"  jobs returned: {len(d3.get('jobs', []))}")
    if d3.get('jobs'):
        j = d3['jobs'][0]
        print(f"  First job keys: {list(j.keys())}")
        print(f"  posted_at: {j.get('posted_at')}")
        print(f"  title: {j.get('title')}")
        print(f"  location: {j.get('location')}")
        print(f"  url: {j.get('url')}")
        print(f"  job_id: {j.get('job_id')}")
        print(f"  id: {j.get('id')}")
        print(f"  employer: {j.get('employer')}")

    # Also check if search/filter params exist
    print("\n=== Test search params ===")
    r4 = client.get(f"{BASE}/api/tools/landing_page/{SLUG}/jobs", params={"page": 1, "per_page": 12, "radius": "40miles"})
    d4 = r4.json()
    print(f"with radius param: jobs_count={d4.get('jobs_count')}, pages_total={d4.get('pages_total')}")

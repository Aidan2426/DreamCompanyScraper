import httpx
import re
import json

HEADERS_BASE = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

BASE = "https://micron.eightfold.ai"
API = f"{BASE}/api/pcsx/search"

with httpx.Client(timeout=30, headers=HEADERS_BASE, follow_redirects=True) as client:
    r0 = client.get(f"{BASE}/careers", params={"start": 0, "sort_by": "timestamp"},
                    headers={**HEADERS_BASE, "Accept": "text/html"})
    csrf = re.search(r'name="_csrf"\s+content="([^"]+)"', r0.text)
    csrf_token = csrf.group(1) if csrf else ""

    api_headers = {
        **HEADERS_BASE,
        "Accept": "application/json",
        "X-CSRFToken": csrf_token,
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"{BASE}/careers?start=0&sort_by=timestamp",
    }

    r = client.get(API, params={"domain": "micron.com", "start": 0, "num": 25, "sort_by": "timestamp"},
                   headers=api_headers)
    d = r.json()
    data = d.get("data", {})
    print("data keys:", list(data.keys()))
    print("count:", data.get("count"))
    print("sortBy:", data.get("sortBy"))

    positions = data.get("positions", [])
    print(f"Positions returned: {len(positions)}")

    if positions:
        p = positions[0]
        print(f"\nFirst position keys: {list(p.keys())}")
        print(json.dumps(p, indent=2))

    # Test pagination
    print("\n=== Page 2 (start=25) ===")
    r2 = client.get(API, params={"domain": "micron.com", "start": 25, "num": 25, "sort_by": "timestamp"},
                    headers=api_headers)
    d2 = r2.json()
    pos2 = d2.get("data", {}).get("positions", [])
    print(f"Positions: {len(pos2)}")

    # Test num=50
    print("\n=== num=50 ===")
    r3 = client.get(API, params={"domain": "micron.com", "start": 0, "num": 50, "sort_by": "timestamp"},
                    headers=api_headers)
    d3 = r3.json()
    pos3 = d3.get("data", {}).get("positions", [])
    print(f"returned: {len(pos3)}")
    print("count:", d3.get("data", {}).get("count"))

    # Test num=100
    print("\n=== num=100 ===")
    r4 = client.get(API, params={"domain": "micron.com", "start": 0, "num": 100, "sort_by": "timestamp"},
                    headers=api_headers)
    d4 = r4.json()
    pos4 = d4.get("data", {}).get("positions", [])
    print(f"returned: {len(pos4)}, count: {d4.get('data',{}).get('count')}")

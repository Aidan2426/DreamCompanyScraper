import httpx
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://apply.hp.com/careers",
}

with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    r = client.get("https://apply.hp.com/api/pcsx/search", params={
        "domain": "hp.com", "query": "", "location": "", "start": 0, "sort_by": "timestamp"
    })
    print("Status:", r.status_code)
    data = r.json()
    positions = data.get("data", {}).get("positions", [])
    total = data.get("data", {}).get("count", "N/A")
    print("Total count:", total)
    print("Page size:", len(positions))

    if positions:
        p = positions[0]
        print("\nAll keys:", list(p.keys()))
        print("\nSample job:")
        for k, v in p.items():
            print(f"  {k}: {repr(v)[:80]}")

    # Try page 2
    r2 = client.get("https://apply.hp.com/api/pcsx/search", params={
        "domain": "hp.com", "query": "", "location": "", "start": 10, "sort_by": "timestamp"
    })
    d2 = r2.json()
    p2 = d2.get("data", {}).get("positions", [])
    print(f"\nPage 2 (start=10): {len(p2)} jobs, first: {p2[0].get('name') if p2 else 'N/A'}")
    print(f"Same as page1 first? {p2[0].get('id') == positions[0].get('id') if p2 else 'N/A'}")

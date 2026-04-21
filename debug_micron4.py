import httpx
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

BASE = "https://micron.eightfold.ai"

with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    r = client.get(f"{BASE}/careers", params={"start": 0, "sort_by": "timestamp"})
    body = r.text
    print(f"Page size: {len(body)} chars")

    # Dump a section of the body to find job structure
    # Find "position" or "job" JSON blobs
    # Look for data-* attributes or script tags with job data

    # Find all <script> tags content
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', body, re.DOTALL)
    print(f"\nScript tags: {len(scripts)}")
    for i, s in enumerate(scripts):
        if len(s) > 100 and any(x in s for x in ['position', 'job', 'title', 'location', 'posted']):
            print(f"\nScript {i} (len={len(s)}):")
            print(s[:800])

    # Find data-json or data-config attributes
    data_attrs = re.findall(r'data-(?:json|config|props|state|jobs|positions)=["\']([^"\']{20,})["\']', body)
    print(f"\nData attrs: {len(data_attrs)}")
    for a in data_attrs[:3]:
        print(a[:400])

    # Look for position card HTML structure
    position_cards = re.findall(r'class="[^"]*position[^"]*"[^>]*>(.*?)</(?:div|li|article)>', body, re.DOTALL)
    print(f"\nPosition cards: {len(position_cards)}")
    for pc in position_cards[:2]:
        print(pc[:400])

    # Look for job title text patterns
    title_hits = re.findall(r'"title"\s*:\s*"([^"]{5,80})"', body)
    print(f"\nTitle hits: {len(title_hits)}")
    for t in title_hits[:10]:
        print(" ", t)

    # Full text search for specific Eightfold patterns
    if 'positions' in body.lower():
        # find context
        idx = body.lower().find('"positions"')
        if idx >= 0:
            print(f"\n'positions' found at {idx}:")
            print(body[idx:idx+500])

    # Check if there's a JSON blob anywhere
    json_blobs = re.findall(r'\{(?:[^{}]|\{[^{}]*\}){0,50}"positions?\w*"\s*:\s*\[', body)
    print(f"\nJSON with positions array: {len(json_blobs)}")
    for b in json_blobs[:2]:
        print(b[:300])

    # Save full HTML for manual inspection
    with open("micron_page.html", "w", encoding="utf-8") as f:
        f.write(body)
    print(f"\nSaved micron_page.html ({len(body)} chars)")

    # Print first 5000 chars of body
    print("\n=== Body start ===")
    print(body[:2000])
    print("\n=== Body end ===")
    print(body[-1000:])

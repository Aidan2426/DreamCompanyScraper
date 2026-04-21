import httpx
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,*/*",
    "Accept-Language": "en-US,en;q=0.9",
}

BASE = "https://jobs.ebayinc.com"

with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    # Sort by most recent - check URL params
    r = client.get(f"{BASE}/us/en/search-results", params={"from": 0, "s": 1})
    body = r.text
    print(f"Page size: {len(body)}, Status: {r.status_code}")

    # Check phApp config
    cfg = re.search(r'var phApp\s*=\s*phApp\s*\|\|\s*(\{.*?\});', body, re.DOTALL)
    if cfg:
        try:
            d = json.loads(cfg.group(1))
            print("phApp config:", json.dumps(d, indent=2)[:500])
        except:
            print("phApp raw:", cfg.group(1)[:300])

    # Extract jobs JSON
    idx = body.find('"jobs":')
    if idx >= 0:
        arr_start = body.index('[', idx)
        depth = 0
        for i in range(arr_start, min(arr_start + 500000, len(body))):
            if body[i] == '[': depth += 1
            elif body[i] == ']':
                depth -= 1
                if depth == 0:
                    jobs = json.loads(body[arr_start:i+1])
                    print(f"\nJobs in HTML: {len(jobs)}")
                    if jobs:
                        j = jobs[0]
                        print("Keys:", list(j.keys()))
                        print("First job:", json.dumps(j, indent=2)[:1500])
                    break
    else:
        print("No 'jobs' array found")

    # Check total
    total_m = re.search(r'"totalHits"\s*:\s*(\d+)', body)
    print(f"\ntotalHits: {total_m.group(1) if total_m else 'not found'}")

    # Check for date-related keys anywhere
    date_keys = re.findall(r'"((?:date|posted|created|time)[^"]{0,20})"\s*:', body, re.IGNORECASE)
    print(f"\nDate-related keys: {sorted(set(date_keys))[:15]}")

    # Try sort by recent
    print("\n=== With sort param ===")
    for params in [
        {"from": 0, "s": 1},
        {"from": 0, "s": 1, "sort": "recent"},
        {"from": 0, "s": 1, "sortColumn": "referencedate", "sortDirection": "desc"},
    ]:
        r2 = client.get(f"{BASE}/us/en/search-results", params=params)
        idx2 = r2.text.find('"jobs":')
        if idx2 >= 0:
            arr_s = r2.text.index('[', idx2)
            depth = 0
            for i in range(arr_s, min(arr_s+500000, len(r2.text))):
                if r2.text[i]=='[': depth+=1
                elif r2.text[i]==']':
                    depth-=1
                    if depth==0:
                        js = json.loads(r2.text[arr_s:i+1])
                        first_keys = list(js[0].keys()) if js else []
                        print(f"params={params}: {len(js)} jobs, keys={first_keys[:8]}")
                        if js:
                            print("  sample:", {k: js[0].get(k) for k in ['reqId','postedDate','dateCreated','datePosted','title','location']})
                        break

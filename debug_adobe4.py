import httpx
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,*/*",
    "Accept-Language": "en-US,en;q=0.9",
}

BASE = "https://careers.adobe.com"

with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    r = client.get(f"{BASE}/us/en/search-results")
    body = r.text

    # Find the jobs JSON blob
    idx = body.find('"jobs":')
    if idx < 0:
        print("No jobs found")
    else:
        # Find enclosing object - walk back to find opening brace
        # The jobs array starts at idx+7
        arr_start = body.index('[', idx)
        # Find matching closing bracket
        depth = 0
        arr_end = arr_start
        for i in range(arr_start, min(arr_start + 500000, len(body))):
            if body[i] == '[':
                depth += 1
            elif body[i] == ']':
                depth -= 1
                if depth == 0:
                    arr_end = i + 1
                    break

        jobs_json = body[arr_start:arr_end]
        try:
            jobs = json.loads(jobs_json)
            print(f"Jobs in HTML: {len(jobs)}")
            if jobs:
                j = jobs[0]
                print(f"\nFirst job keys: {list(j.keys())}")
                print(f"\nFirst job:")
                print(json.dumps(j, indent=2)[:2000])
        except Exception as e:
            print(f"Parse error: {e}")
            print("Raw (500):", jobs_json[:500])

    # Check total count
    total_m = re.search(r'"totalJobsCount"\s*:\s*(\d+)', body)
    if total_m:
        print(f"\ntotalJobsCount: {total_m.group(1)}")
    total_m2 = re.search(r'"total"\s*:\s*(\d+)', body)
    if total_m2:
        print(f"total: {total_m2.group(1)}")
    # Search for count
    counts = re.findall(r'"(?:total|count|jobCount|totalCount|numFound|totalJobs)[A-Za-z]*"\s*:\s*(\d+)', body)
    print(f"Count values: {counts[:10]}")

    # Check page 2 with from=10
    print("\n=== Page 2 (from=10) ===")
    r2 = client.get(f"{BASE}/us/en/search-results", params={"from": 10, "s": 1})
    body2 = r2.text
    idx2 = body2.find('"jobs":')
    if idx2 >= 0:
        arr_start2 = body2.index('[', idx2)
        depth = 0
        arr_end2 = arr_start2
        for i in range(arr_start2, min(arr_start2 + 500000, len(body2))):
            if body2[i] == '[':
                depth += 1
            elif body2[i] == ']':
                depth -= 1
                if depth == 0:
                    arr_end2 = i + 1
                    break
        jobs2 = json.loads(body2[arr_start2:arr_end2])
        print(f"Jobs on page 2: {len(jobs2)}")
        if jobs2:
            print("First job reqId:", jobs2[0].get("reqId"))

    # Try larger from values
    print("\n=== from=100 ===")
    r3 = client.get(f"{BASE}/us/en/search-results", params={"from": 100, "s": 1})
    idx3 = r3.text.find('"jobs":')
    if idx3 >= 0:
        arr_s = r3.text.index('[', idx3)
        depth = 0
        for i in range(arr_s, min(arr_s + 500000, len(r3.text))):
            if r3.text[i] == '[': depth += 1
            elif r3.text[i] == ']':
                depth -= 1
                if depth == 0:
                    print(f"Jobs at from=100: {len(json.loads(r3.text[arr_s:i+1]))}")
                    break

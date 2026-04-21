import httpx
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, */*",
    "Referer": "https://jobs.universalparks.com/",
}

url = "https://jobsapi-internal.m-cloud.io/api/job"

# Try large limit to get all jobs at once
params = {
    "sortfield": "open_date",
    "sortorder": "descending",
    "Limit": 250,
    "Organization": 1717,
    "offset": 1,
}

with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    r = client.get(url, params=params)
    print("Status:", r.status_code)
    print("CT:", r.headers.get("content-type", ""))

    text = r.text
    # Strip JSONP wrapper if present
    m = re.match(r"^[^(]+\((.+)\)$", text.strip(), re.DOTALL)
    if m:
        data = json.loads(m.group(1))
    else:
        data = r.json()

    print("totalHits:", data.get("totalHits"))
    jobs = data.get("queryResult", [])
    print("Jobs returned:", len(jobs))

    if jobs:
        print("\nAll keys in first job:")
        for k, v in jobs[0].items():
            print(f"  {k}: {repr(v)[:80]}")

        print("\nSample job (relevant fields):")
        j = jobs[0]
        for k in ["title", "city", "state", "country", "location", "open_date", "post_date", "posted_date", "company_name", "id", "function", "industry"]:
            if k in j:
                print(f"  {k}: {j[k]}")

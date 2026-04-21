import httpx
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Referer": "https://intel.wd1.myworkdayjobs.com/External",
}

# Workday CXS API - standard pattern
url = "https://intel.wd1.myworkdayjobs.com/wday/cxs/intel/External/jobs"
payload = {
    "appliedFacets": {},
    "limit": 20,
    "offset": 0,
    "searchText": "",
}

with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    # First GET the page to pick up cookies/CSRF
    r0 = client.get("https://intel.wd1.myworkdayjobs.com/External")
    print("GET status:", r0.status_code)
    print("Cookies:", list(client.cookies.keys()))

    # Now POST
    r = client.post(url, json=payload)
    print("POST status:", r.status_code)
    print("CT:", r.headers.get("content-type", ""))
    if r.status_code == 200:
        data = r.json()
        print("Keys:", list(data.keys()))
        jobs = data.get("jobPostings", [])
        total = data.get("total", 0)
        print("Total:", total)
        print("Jobs returned:", len(jobs))
        if jobs:
            j = jobs[0]
            print("Job keys:", list(j.keys()))
            print("Sample:", {k: j.get(k) for k in ["title", "locationsText", "postedOn", "bulletFields", "externalPath", "timeType"]})
    else:
        print("Body:", r.text[:500])

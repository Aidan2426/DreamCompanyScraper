import httpx
import json
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    # Step 1: get the page to get cookies + CSRF token
    r = client.get("https://ibm.wd3.myworkdayjobs.com/IBMExternalSite")
    print("GET status:", r.status_code)
    print("Cookies:", dict(client.cookies))

    # Look for CSRF token in HTML
    csrf = re.search(r'wd-csrf-token["\s:]+([A-Za-z0-9_\-]+)', r.text)
    if csrf:
        print("CSRF:", csrf.group(1))

    # Step 2: POST to jobs API
    post_headers = {
        **HEADERS,
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Referer": "https://ibm.wd3.myworkdayjobs.com/IBMExternalSite",
    }
    # Add CSRF if found
    if csrf:
        post_headers["X-Workday-Client-Request-ID"] = csrf.group(1)

    payload = {
        "appliedFacets": {},
        "limit": 20,
        "offset": 0,
        "searchText": ""
    }

    r2 = client.post(
        "https://ibm.wd3.myworkdayjobs.com/wday/cxs/ibm/IBMExternalSite/jobs",
        json=payload,
        headers=post_headers
    )
    print("POST status:", r2.status_code)
    print("Content-Type:", r2.headers.get("content-type", ""))
    print("Body:", r2.text[:1000])

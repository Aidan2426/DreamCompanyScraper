import httpx
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.ibm.com/careers/search?sort=dcdate_desc",
}

# IBM careers uses a search API - let's try to find it
# Based on the scopeid 'careers2' and appid 'careers' found in the HTML

candidates = [
    # IBM marketplace search API
    ("GET", "https://www.ibm.com/search/api/v3/search?q=&lang=en&cc=us&appid=careers&scopeid=careers2&sort=dcdate_desc&rows=25&start=0"),
    ("GET", "https://www.ibm.com/search/api/v2/search?q=&lang=en&cc=us&appid=careers&sort=dcdate_desc&rows=25&start=0"),
    ("GET", "https://www.ibm.com/marketplace/api/search?q=&appid=careers&sort=dcdate_desc&rows=25&start=0"),
    ("GET", "https://www.ibm.com/search?q=&appid=careers&sort=dcdate_desc&rows=25&start=0"),
    # Direct careers API
    ("GET", "https://www.ibm.com/careers/search?q=&sort=dcdate_desc&rows=25&start=0&format=json"),
    ("GET", "https://careers.ibm.com/en_US/careers/search?q=&sort=dcdate_desc&rows=25&start=0"),
    ("GET", "https://careers.ibm.com/en_US/careers/search?q=&sort=dcdate_desc&start=0&format=json"),
]

with httpx.Client(timeout=15, headers=HEADERS, follow_redirects=True) as client:
    for method, url in candidates:
        try:
            r = client.get(url)
            ct = r.headers.get("content-type", "")
            print(f"{r.status_code} | {ct[:40]} | {url[:80]}")
            if r.status_code == 200 and "json" in ct:
                print("  JSON:", r.text[:400])
            elif r.status_code == 200 and len(r.text) < 500:
                print("  Body:", r.text[:200])
        except Exception as e:
            print(f"ERR | {url[:80]} | {e}")

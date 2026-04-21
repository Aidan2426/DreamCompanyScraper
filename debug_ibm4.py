import httpx
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, */*",
    "Referer": "https://www.ibm.com/careers/search?sort=dcdate_desc",
    "X-Requested-With": "XMLHttpRequest",
}

# IBM uses its common search platform - try known patterns
candidates = [
    # Common IBM search API with careers scope
    "https://www.ibm.com/search?lang=en&cc=us&q=&fq=appid%3Acareers&dord=dcdate_desc&rows=25&start=0",
    "https://www.ibm.com/search?lang=en&cc=us&q=&appid=careers&sort=dcdate_desc&rows=25&start=0",
    # IBM talent/careers specific
    "https://www.ibm.com/careers/api/jobs?sort=dcdate_desc&rows=25&start=0",
    "https://www.ibm.com/careers/api/search?sort=dcdate_desc&rows=25&start=0&format=json",
    # Phenom People (IBM used this)
    "https://ibm.wd3.myworkdayjobs.com/wday/cxs/ibm/IBMExternalSite/jobs",
    "https://ibm.wd3.myworkdayjobs.com/IBMExternalSite",
    # Try with JSON accept header
    "https://www.ibm.com/careers/search?sort=dcdate_desc&rows=25&start=0",
]

with httpx.Client(timeout=15, headers=HEADERS, follow_redirects=True) as client:
    for url in candidates:
        try:
            r = client.get(url)
            ct = r.headers.get("content-type", "")
            preview = r.text[:200].replace("\n", " ")
            print(f"{r.status_code} | {ct[:35]} | {url[:70]}")
            if "json" in ct or r.status_code in [200, 201]:
                print(f"  preview: {preview[:150]}")
        except Exception as e:
            print(f"ERR | {url[:70]} | {e}")

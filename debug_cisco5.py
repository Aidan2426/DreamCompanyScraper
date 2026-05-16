import httpx
import json
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def extract_jobs(html: str):
    idx = html.find('"eagerLoadRefineSearch":{')
    if idx < 0:
        # try alternate key
        idx = html.find('"eagerLoadRefineSearchSession":{')
        if idx < 0:
            return [], 0
        start = idx + len('"eagerLoadRefineSearchSession":')
    else:
        start = idx + len('"eagerLoadRefineSearch":')

    depth = 0
    end = start
    for i, ch in enumerate(html[start:], start):
        if ch == "{": depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break

    data = json.loads(html[start:end])
    total = data.get("totalHits", 0)
    jobs = data.get("data", {}).get("jobs", [])
    return jobs, total


with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    # Test page 1
    r1 = client.get("https://careers.cisco.com/global/en/search-results")
    jobs1, total = extract_jobs(r1.text)
    print(f"Page 1: {len(jobs1)} jobs, total={total}")
    if jobs1:
        print("  First:", jobs1[0].get("title"), "|", jobs1[0].get("location"), "|", jobs1[0].get("postedDate"))

    # Test page 2 (s=1)
    r2 = client.get("https://careers.cisco.com/global/en/search-results?s=1")
    jobs2, _ = extract_jobs(r2.text)
    print(f"Page 2: {len(jobs2)} jobs")
    if jobs2:
        print("  First:", jobs2[0].get("title"), "|", jobs2[0].get("location"), "|", jobs2[0].get("postedDate"))

    # Verify no overlap
    ids1 = {j.get("reqId") for j in jobs1}
    ids2 = {j.get("reqId") for j in jobs2}
    print(f"Overlap between page 1 and 2: {ids1 & ids2}")

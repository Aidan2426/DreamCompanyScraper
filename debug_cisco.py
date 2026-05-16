import re
import json
import httpx

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
}

with open("debug_cisco.html", encoding="utf-8") as f:
    html = f.read()

# Extract first page data
idx = html.find('"eagerLoadRefineSearch":{')
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
job = data["data"]["jobs"][0]
print("postedDate:", job.get("postedDate"))
print("dateCreated:", job.get("dateCreated"))
print("location:", job.get("location"))
print("cityStateCountry:", job.get("cityStateCountry"))

# Try Phenom People widget API
# Standard pattern: /widgets/api/jobs?... or /api/jobs?...
candidates = [
    "https://careers.cisco.com/api/jobs?limit=10&offset=10&lang=en_global&country=global",
    "https://careers.cisco.com/widgets/api/jobs?limit=10&offset=10&lang=en_global",
    "https://careers.cisco.com/global/en/search-results?limit=10&offset=10&format=json",
]

with httpx.Client(timeout=15, headers=HEADERS, follow_redirects=True) as client:
    for url in candidates:
        try:
            r = client.get(url)
            ct = r.headers.get("content-type", "")
            print(f"\n{r.status_code} | {ct[:40]} | {url[:80]}")
            if "json" in ct:
                print("  JSON:", r.text[:300])
        except Exception as e:
            print(f"ERR: {e}")

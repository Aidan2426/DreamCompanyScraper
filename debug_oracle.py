import httpx
from bs4 import BeautifulSoup
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    r = client.get("https://careers.oracle.com/en/sites/jobsearch/jobs?mode=location")
    print("Status:", r.status_code)
    print("Final URL:", r.url)
    with open("debug_oracle.html", "w", encoding="utf-8") as f:
        f.write(r.text)
    print("Length:", len(r.text))

    soup = BeautifulSoup(r.text, "lxml")
    print("Title:", soup.title.get_text() if soup.title else "none")

    # Check __NEXT_DATA__
    nd = soup.find("script", id="__NEXT_DATA__")
    if nd:
        print("Has __NEXT_DATA__")
        data = json.loads(nd.get_text())
        print(json.dumps(data, indent=2)[:2000])

    # Look for job listings in HTML
    for tag in ["div", "li", "article"]:
        candidates = soup.find_all(tag, class_=lambda c: c and any(
            k in " ".join(c).lower() for k in ["job", "result", "card", "position", "listing", "requisition"]
        ))
        if candidates:
            print(f"<{tag}> count={len(candidates)} classes={candidates[0].get('class')}")
            print(str(candidates[0])[:400])
            print()

    # API hints
    for kw in ["api", "graphql", "jobs", "requisition", "fetch", "endpoint"]:
        hits = re.findall(rf".{{0,30}}{kw}.{{0,80}}", r.text, re.IGNORECASE)
        if hits:
            print(f"--- {kw} ---")
            for h in list(dict.fromkeys(hits))[:4]:
                print(" ", h[:120])

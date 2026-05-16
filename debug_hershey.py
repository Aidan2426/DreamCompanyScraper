import httpx
from bs4 import BeautifulSoup

BASE_URL = "https://careers.thehersheycompany.com"
SEARCH_URL = f"{BASE_URL}/search/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

params = {
    "createNewAlert": "false",
    "q": "",
    "optionsFacetsDD_country": "",
    "optionsFacetsDD_location": "",
    "optionsFacetsDD_city": "",
    "optionsFacetsDD_title": "",
    "optionsFacetsDD_customfield1": "",
    "optionsFacetsDD_customfield2": "",
}

with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    r = client.get(SEARCH_URL, params=params)
    r.raise_for_status()
    print("Status:", r.status_code)
    print("Final URL:", r.url)

    soup = BeautifulSoup(r.text, "lxml")

    # Save raw HTML
    with open("debug_hershey.html", "w", encoding="utf-8") as f:
        f.write(r.text)
    print("Saved debug_hershey.html")

    # Look for job listings
    print("\n--- Possible job containers ---")
    for tag in ["li", "article", "div"]:
        candidates = soup.find_all(tag, class_=lambda c: c and any(
            k in c.lower() for k in ["job", "result", "position", "listing"]
        ))
        if candidates:
            print(f"<{tag}> with job-related classes: {len(candidates)}")
            print("  First element classes:", candidates[0].get("class"))
            print("  First element snippet:", str(candidates[0])[:300])
            print()

    # Look for pagination
    print("--- Pagination ---")
    for tag in ["a", "input", "span", "div"]:
        pag = soup.find_all(tag, class_=lambda c: c and "pag" in c.lower())
        if pag:
            print(f"<{tag}> pagination elements: {len(pag)}")
            for p in pag[:3]:
                print(" ", str(p)[:200])

    # Look for total count
    print("\n--- Total count text ---")
    for el in soup.find_all(string=lambda s: s and "312" in s or (s and "job" in s.lower() and any(c.isdigit() for c in s))):
        print(repr(el[:200]))

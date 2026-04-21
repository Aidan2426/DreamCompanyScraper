import re
import time
import httpx
from bs4 import BeautifulSoup

SEARCH_URL = "https://careers.paramount.com/search/"
TILES_URL = "https://careers.paramount.com/search/tile-search-results/"
BASE_URL = "https://careers.paramount.com"
PAGE_SIZE = 25
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://careers.paramount.com/search/",
    "X-Requested-With": "XMLHttpRequest",
}


def _parse_tiles(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    jobs = []

    for tile in soup.find_all("li", class_=re.compile(r"\bjob-tile\b")):
        # Job ID + URL
        job_url = tile.get("data-url", "")
        job_id_match = re.search(r"/(\d+)/?$", job_url)
        job_id = job_id_match.group(1) if job_id_match else ""
        if not job_id:
            continue

        # Only parse desktop section to avoid duplicate mobile entries
        desktop = tile.find("div", class_=re.compile(r"\bsub-section-desktop\b"))
        if not desktop:
            continue

        title_el = desktop.find("a", class_="jobTitle-link")
        title = title_el.get_text(strip=True) if title_el else ""
        if not title:
            continue

        def _field(name: str) -> str:
            el = desktop.find("div", id=re.compile(rf"desktop-section-{name}-value"))
            return el.get_text(strip=True) if el else ""

        jobs.append({
            "role_id":     f"paramount_{job_id}",
            "title":       title,
            "team":        _field("customfield1"),   # Job Function
            "location":    _field("location"),
            "posted_date": _field("date"),
            "url":         f"{BASE_URL}{job_url}",
            "company":     "Paramount",
        })

    return jobs


def scrape() -> list[dict]:
    all_jobs: list[dict] = []
    seen: set[str] = set()

    with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
        # Seed cookies + get total count
        r0 = client.get(SEARCH_URL,
                        params={"q": "", "sortColumn": "referencedate", "sortDirection": "desc"},
                        headers={**HEADERS, "Accept": "text/html", "X-Requested-With": ""})
        r0.raise_for_status()
        total_match = re.search(r"Showing\s+\d+\s+to\s+\d+\s+of\s+(\d+)", r0.text)
        total = int(total_match.group(1)) if total_match else None
        total_pages = -(-total // PAGE_SIZE) if total else "?"
        print(f"[paramount] Total: {total}, pages: {total_pages}")

        startrow = 0
        page = 1

        while True:
            r = client.get(TILES_URL, params={
                "q": "", "sortColumn": "referencedate", "sortDirection": "desc", "startrow": startrow
            })
            r.raise_for_status()
            jobs = _parse_tiles(r.text)

            new = [j for j in jobs if j["role_id"] not in seen]
            for j in new:
                seen.add(j["role_id"])
            all_jobs.extend(new)
            print(f"[paramount] Page {page}/{total_pages}: {len(new)} jobs (total {len(all_jobs)})")

            if len(jobs) < PAGE_SIZE:
                break

            startrow += PAGE_SIZE
            page += 1
            time.sleep(0.3)

    print(f"[paramount] Done. {len(all_jobs)} total jobs.")
    return all_jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

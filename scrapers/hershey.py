import math
import time
import httpx
from bs4 import BeautifulSoup

BASE_URL = "https://careers.thehersheycompany.com"
SEARCH_URL = f"{BASE_URL}/search/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
PARAMS = {
    "createNewAlert": "false",
    "q": "",
    "sortColumn": "referencedate",
    "sortDirection": "desc",
}
PAGE_SIZE = 25


def _parse_page(html: str) -> tuple[list[dict], int]:
    soup = BeautifulSoup(html, "html.parser")
    jobs = []

    table = soup.find("table", id="searchresults")
    if not table:
        return jobs, 0

    for row in table.find_all("tr", class_="data-row"):
        a = row.find("a", class_="jobTitle-link")
        if not a:
            continue

        title = a.get_text(strip=True)
        href = a.get("href", "")
        url = f"{BASE_URL}{href}" if href.startswith("/") else href

        # Extract job ID from URL path segment
        job_id = href.rstrip("/").split("/")[-1] if href else ""

        loc_el = row.find("td", class_="colLocation")
        location = loc_el.find("span", class_="jobLocation").get_text(strip=True) if loc_el else ""

        date_el = row.find("td", class_="colDate")
        posted_date = date_el.find("span", class_="jobDate").get_text(strip=True) if date_el else ""

        jobs.append({
            "role_id":     f"hershey_{job_id}",
            "title":       title,
            "team":        "",
            "location":    location,
            "posted_date": posted_date,
            "url":         url,
            "company":     "Hershey",
        })

    # Total count from pagination label
    pag_label = soup.find("span", class_="paginationLabel")
    total = 0
    if pag_label:
        b_tags = pag_label.find_all("b")
        if len(b_tags) >= 2:
            try:
                total = int(b_tags[-1].get_text(strip=True).replace(",", ""))
            except ValueError:
                pass

    total_pages = math.ceil(total / PAGE_SIZE) if total else 1
    return jobs, total_pages


def scrape() -> list[dict]:
    all_jobs: list[dict] = []
    seen: set[str] = set()

    with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
        r = client.get(SEARCH_URL, params=PARAMS)
        r.raise_for_status()
        jobs, total_pages = _parse_page(r.text)

        new = [j for j in jobs if j["role_id"] not in seen]
        for j in new:
            seen.add(j["role_id"])
        all_jobs.extend(new)
        print(f"[hershey] Page 1/{total_pages}: {len(new)} jobs")

        for page in range(2, total_pages + 1):
            time.sleep(0.3)
            p = {**PARAMS, "startrow": (page - 1) * PAGE_SIZE}
            r = client.get(SEARCH_URL, params=p)
            r.raise_for_status()
            jobs, _ = _parse_page(r.text)

            new = [j for j in jobs if j["role_id"] not in seen]
            for j in new:
                seen.add(j["role_id"])
            all_jobs.extend(new)
            print(f"[hershey] Page {page}/{total_pages}: {len(new)} jobs (total {len(all_jobs)})")

            if not new:
                break

    print(f"[hershey] Done. {len(all_jobs)} total jobs.")
    return all_jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

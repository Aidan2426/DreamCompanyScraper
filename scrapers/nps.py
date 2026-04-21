import math
import re
import time
import httpx

SEARCH_URL = "https://nps.usajobs.gov/Search/ExecuteSearch"
PAGE_URL = "https://nps.usajobs.gov/search/results/"
PAGE_SIZE = 25
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://nps.usajobs.gov/search/results/?a=IN10&s=startdate&sd=desc&p=1",
    "Content-Type": "application/json",
}
BRANDED_BASE = {
    "Agency": ["IN10"],
    "SelectedFilters": ["organization"],
    "CurrentOpenPositionsOnly": True,
    "SortField": "startdate",
    "SortDirection": "desc",
    "IncludeInternal": True,
    "HiringPathExcludes": ["nopublic", "fed-internal-nosearch"],
    "ResultsPerPage": PAGE_SIZE,
    "LocationRadius": 25,
}


def _parse_date(date_display: str) -> str:
    """Extract open date from 'Open MM/DD/YYYY to MM/DD/YYYY'."""
    m = re.search(r"Open\s+(\d{2}/\d{2}/\d{4})", date_display or "")
    if m:
        try:
            from datetime import datetime
            return datetime.strptime(m.group(1), "%m/%d/%Y").strftime("%b %d, %Y")
        except Exception:
            return m.group(1)
    return ""


def _parse(data: dict) -> tuple[list[dict], int]:
    total_str = data.get("Total", "0")
    try:
        total = int(total_str)
    except (ValueError, TypeError):
        total = 0

    jobs = []
    for j in data.get("Jobs", []):
        job_id = j.get("DocumentID", "")
        title = (j.get("Title") or "").strip()
        if not title or not job_id:
            continue

        uri = j.get("PositionURI", "")
        url = uri.replace(":443", "") if uri else f"https://www.usajobs.gov/job/{job_id}"

        jobs.append({
            "role_id":     f"nps_{job_id}",
            "title":       title,
            "team":        j.get("Department", ""),
            "location":    j.get("Location", ""),
            "posted_date": _parse_date(j.get("DateDisplay", "")),
            "url":         url,
            "company":     "National Park Service",
            "experience":  j.get("SalaryDisplay", ""),
        })
    return jobs, total


def scrape() -> list[dict]:
    all_jobs: list[dict] = []
    seen: set[str] = set()

    with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
        # Seed session cookies
        client.get(PAGE_URL, params={"a": "IN10", "s": "startdate", "sd": "desc", "p": 1},
                   headers={**HEADERS, "Accept": "text/html", "X-Requested-With": ""})

        page = 1
        total = None
        total_pages = None

        while True:
            payload = {**BRANDED_BASE, "Page": page}
            r = client.post(SEARCH_URL, json=payload)
            r.raise_for_status()
            jobs, page_total = _parse(r.json())

            if total is None and page_total > 0:
                total = page_total
                total_pages = math.ceil(total / PAGE_SIZE)
                print(f"[nps] Total: {total}, pages: {total_pages}")

            new = [j for j in jobs if j["role_id"] not in seen]
            for j in new:
                seen.add(j["role_id"])
            all_jobs.extend(new)
            print(f"[nps] Page {page}/{total_pages}: {len(new)} jobs (total {len(all_jobs)})")

            if not jobs or page >= total_pages:
                break

            page += 1
            time.sleep(0.3)

    print(f"[nps] Done. {len(all_jobs)} total jobs.")
    return all_jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

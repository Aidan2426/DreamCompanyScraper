import math
import re
import time
import httpx
from bs4 import BeautifulSoup

BASE_URL  = "https://jobs.ea.com"
LIST_URL  = f"{BASE_URL}/en_US/careers/Home/"
PAGE_SIZE = 20
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,*/*",
}


def _parse_page(html: str) -> tuple[list[dict], int]:
    soup = BeautifulSoup(html, "html.parser")

    total = 0
    m = re.search(r"of\s+([\d,]+)", html)
    if m:
        try:
            total = int(m.group(1).replace(",", ""))
        except ValueError:
            pass

    jobs = []
    for article in soup.find_all("article"):
        link = article.find("a", class_="link_result")
        if not link:
            continue
        title = link.get_text(strip=True)
        url   = link.get("href", "")

        job_id_m = re.search(r"/(\d+)$", url)
        job_id   = job_id_m.group(1) if job_id_m else url

        location = ""
        loc_tag  = article.find("span", class_="list-item-location")
        if loc_tag:
            location = loc_tag.get_text(strip=True)

        dept = ""
        dept_tag = article.find("span", class_="list-item-department")
        if dept_tag:
            dept = dept_tag.get_text(strip=True)

        jobs.append({
            "role_id":     f"ea_{job_id}",
            "title":       title,
            "team":        dept,
            "location":    location,
            "posted_date": "",
            "url":         url,
            "company":     "EA",
            "experience":  "",
        })

    return jobs, total


def scrape() -> list[dict]:
    all_jobs: list[dict] = []
    seen: set[str] = set()

    with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
        offset = 0
        total = None
        total_pages = None
        page = 1

        while True:
            params = {"jobRecordsPerPage": PAGE_SIZE, "jobOffset": offset}
            r = client.get(LIST_URL, params=params)
            r.raise_for_status()
            jobs, page_total = _parse_page(r.text)

            if total is None and page_total > 0:
                total = page_total
                total_pages = math.ceil(total / PAGE_SIZE)
                print(f"[ea] Total: {total}, pages: {total_pages}")

            new = [j for j in jobs if j["role_id"] not in seen]
            for j in new:
                seen.add(j["role_id"])
            all_jobs.extend(new)
            print(f"[ea] Page {page}/{total_pages}: {len(new)} jobs (total {len(all_jobs)})")

            if not jobs or (total and offset + PAGE_SIZE >= total):
                break

            offset += PAGE_SIZE
            page += 1
            time.sleep(0.4)

    print(f"[ea] Done. {len(all_jobs)} total jobs.")
    return all_jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

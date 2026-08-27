import time
import httpx
from bs4 import BeautifulSoup

BASE_URL = "https://www.disneycareers.com"
SEARCH_URL = f"{BASE_URL}/en/search-jobs/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def _parse_page(html: str) -> tuple[list[dict], int]:
    soup = BeautifulSoup(html, "html.parser")
    jobs = []

    for a in soup.find_all("a", attrs={"data-job-id": True}):
        job_id = a.get("data-job-id", "").strip()
        if not job_id:
            continue

        title_el = a.find("h2") or a.find("h3")
        title = title_el.get_text(strip=True) if title_el else ""
        if not title:
            continue

        brand_el = a.find("span", class_="job-brand")
        loc_el   = a.find("span", class_="job-location")
        date_el  = a.find("span", class_="job-date-posted")

        team        = brand_el.get_text(strip=True) if brand_el else ""
        location    = loc_el.get_text(strip=True)   if loc_el   else ""
        posted_date = date_el.get_text(strip=True)  if date_el  else ""

        href = a.get("href", "")
        url  = f"{BASE_URL}{href}" if href.startswith("/") else href

        jobs.append({
            "role_id":     f"disney_{job_id}",
            "title":       title,
            "team":        team,
            "location":    location,
            "posted_date": posted_date,
            "url":         url,
            "company":     "Disney",
        })

    pag_input   = soup.find("input", class_="pagination-current")
    total_pages = int(pag_input.get("max", 1)) if pag_input else 1

    return jobs, total_pages


def scrape() -> list[dict]:
    all_jobs: list[dict] = []
    seen: set[str] = set()

    with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
        r = client.get(SEARCH_URL)
        r.raise_for_status()
        jobs, total_pages = _parse_page(r.text)

        new = [j for j in jobs if j["role_id"] not in seen]
        for j in new:
            seen.add(j["role_id"])
        all_jobs.extend(new)
        print(f"[disney] Page 1/{total_pages}: {len(new)} jobs")

        for page in range(2, total_pages + 1):
            time.sleep(0.3)
            r = client.get(SEARCH_URL, params={"p": page})
            r.raise_for_status()
            jobs, _ = _parse_page(r.text)

            new = [j for j in jobs if j["role_id"] not in seen]
            for j in new:
                seen.add(j["role_id"])
            all_jobs.extend(new)
            print(f"[disney] Page {page}/{total_pages}: {len(new)} jobs (total {len(all_jobs)})")

            if not new:
                break

    print(f"[disney] Done. {len(all_jobs)} total jobs.")
    return all_jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

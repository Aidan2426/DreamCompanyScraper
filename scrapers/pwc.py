import httpx
import time
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = "https://jobs.us.pwc.com/search-jobs/results"
JOB_BASE = "https://jobs.us.pwc.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://jobs.us.pwc.com/search-jobs",
}
BASE_PARAMS = "ActiveFacetID=0&RecordsPerPage=15&Distance=50&RadiusUnitType=0&Keywords=&Location=&ShowRadius=False&IsPagination=False&CustomFacetName=&FacetTerm=&FacetType=0&SearchResultsModuleName=Search+Results&SearchFiltersModuleName=Search+Filters&SortCriteria=0&SortDirection=Ascending&SearchType=5&PostalCode=&ResultsType=0&fc=&fl=&fr="


def _fmt_date(raw: str) -> str:
    try:
        return datetime.strptime(raw.strip(), "%m/%d/%Y").strftime("%b %d, %Y")
    except Exception:
        return raw.strip()


def scrape() -> list[dict]:
    all_jobs = []
    seen = set()

    with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
        page = 1
        total_pages = None

        while True:
            url = f"{BASE_URL}?{BASE_PARAMS}&CurrentPage={page}"
            r = client.get(url)
            r.raise_for_status()
            html = r.json().get("results", "")
            soup = BeautifulSoup(html, "html.parser")

            if total_pages is None:
                section = soup.find(attrs={"data-total-pages": True})
                total_pages = int(section["data-total-pages"]) if section else 30
                total_jobs = section["data-total-results"] if section else "?"
                print(f"[pwc] {total_jobs} jobs across {total_pages} pages")

            cards = soup.find_all("li")
            if not cards:
                break

            for li in cards:
                a = li.find("a", attrs={"data-job-id": True})
                if not a:
                    continue
                job_id = a.get("data-job-id", "")
                if not job_id or job_id in seen:
                    continue
                seen.add(job_id)

                title    = a.find("h2")
                location = a.find("span", class_="job-location")
                category = a.find("span", class_="job-category")
                date_el  = a.find("span", class_="job-date-posted")
                href     = a.get("href", "")

                all_jobs.append({
                    "role_id":     f"pwc_{job_id}",
                    "title":       title.get_text(strip=True) if title else "",
                    "team":        category.get_text(strip=True) if category else "",
                    "location":    location.get_text(strip=True) if location else "",
                    "posted_date": _fmt_date(date_el.get_text()) if date_el else "",
                    "url":         JOB_BASE + href if href.startswith("/") else href,
                    "company":     "PwC",
                })

            print(f"[pwc] Page {page}/{total_pages}: {len(cards)} cards (total {len(all_jobs)})")

            if page >= total_pages:
                break
            page += 1
            time.sleep(0.5)

    print(f"[pwc] Done. {len(all_jobs)} jobs.")
    return all_jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

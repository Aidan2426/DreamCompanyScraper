import httpx
import time
import random
from bs4 import BeautifulSoup

# LinkedIn company IDs to scrape. Add/remove as needed.
# Find a company's ID from their LinkedIn jobs URL: ?f_C=XXXXX
COMPANY_IDS = [
    1337,    # LinkedIn
]

BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}
PAGE_SIZE = 10
MAX_EMPTY_PAGES = 3  # stop after this many consecutive pages with 0 new unique jobs


def _scrape_company(client: httpx.Client, company_id: int) -> list[dict]:
    jobs = []
    seen = set()
    pos = 1
    empty_streak = 0

    while True:
        try:
            r = client.get(BASE_URL, params={
                "f_C": company_id,
                "geoId": 92000000,
                "position": pos,
                "pageNum": 0,
            })
            r.raise_for_status()
        except Exception as e:
            print(f"[linkedin] company {company_id} pos={pos} error: {e}")
            break

        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.find_all("div", class_="base-card")
        if not cards:
            break

        new_this_page = 0
        for card in cards:
            urn = card.get("data-entity-urn", "")
            raw_id = urn.split(":")[-1] if urn else ""
            if not raw_id or raw_id in seen:
                continue
            seen.add(raw_id)
            new_this_page += 1

            title_el   = card.find("h3", class_="base-search-card__title")
            company_el = card.find("h4", class_="base-search-card__subtitle")
            loc_el     = card.find("span", class_="job-search-card__location")
            time_el    = card.find("time", class_="job-search-card__listdate")
            url_el     = card.find("a", class_="base-card__full-link")

            title   = title_el.get_text(strip=True) if title_el else ""
            company = company_el.get_text(strip=True) if company_el else "LinkedIn"
            loc     = loc_el.get_text(strip=True) if loc_el else ""
            date    = time_el.get("datetime", "") if time_el else ""
            url     = url_el.get("href", "").split("?")[0] if url_el else ""

            if not title:
                continue

            jobs.append({
                "role_id":     f"linkedin_{raw_id}",
                "title":       title,
                "team":        "",
                "location":    loc,
                "posted_date": date,
                "url":         url,
                "company":     company,
            })

        print(f"[linkedin] company={company_id} pos={pos}: {new_this_page} new (total {len(jobs)})")

        if new_this_page == 0:
            empty_streak += 1
            if empty_streak >= MAX_EMPTY_PAGES:
                print(f"[linkedin] company={company_id}: {MAX_EMPTY_PAGES} pages with no new jobs, stopping")
                break
        else:
            empty_streak = 0

        if len(cards) < PAGE_SIZE:
            break

        pos += PAGE_SIZE
        time.sleep(1.5 + random.random())  # 1.5–2.5s to avoid 429

    return jobs


def scrape() -> list[dict]:
    all_jobs = []
    with httpx.Client(timeout=20, headers=HEADERS, follow_redirects=True) as client:
        for company_id in COMPANY_IDS:
            jobs = _scrape_company(client, company_id)
            all_jobs.extend(jobs)
            print(f"[linkedin] company={company_id} done: {len(jobs)} jobs")
            time.sleep(1)

    print(f"[linkedin] Total: {len(all_jobs)} jobs")
    return all_jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

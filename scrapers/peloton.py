import asyncio
import re
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup

BASE_URL  = "https://careers.onepeloton.com"
SEARCH    = "/en/all-jobs/"
HEADERS   = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
CONCURRENCY = 3


async def _fetch_page(session: AsyncSession, sem: asyncio.Semaphore, page: int) -> str:
    async with sem:
        params = {"page": page} if page > 1 else {}
        r = await session.get(BASE_URL + SEARCH, params=params, headers=HEADERS, timeout=30)
        r.raise_for_status()
        return r.text


def _parse_page(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    for card in soup.select("#js-job-search-results .card-job"):
        title_a  = card.select_one("h3.card-title a")
        cat_el   = card.select_one("span.card-category")
        loc_li   = card.select_one("ul.job-meta li")
        id_el    = card.select_one("div.card-job-actions[data-id]")

        if not title_a or not id_el:
            continue

        job_id = id_el["data-id"].strip()
        title  = title_a.get_text(strip=True)
        href   = title_a["href"]
        url    = BASE_URL + href if href.startswith("/") else href
        team   = cat_el.get_text(strip=True) if cat_el else ""
        loc    = loc_li.get_text(strip=True) if loc_li else ""

        jobs.append({
            "role_id":     f"peloton_{job_id}",
            "title":       title,
            "team":        team,
            "location":    loc,
            "posted_date": "",
            "url":         url,
            "company":     "Peloton",
        })
    return jobs


def _total_pages(html: str) -> int:
    soup  = BeautifulSoup(html, "html.parser")
    pages = soup.select(".pagination a[href*='page=']")
    nums  = []
    for a in pages:
        m = re.search(r"page=(\d+)", a["href"])
        if m:
            nums.append(int(m.group(1)))
    return max(nums) if nums else 1


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        sem   = asyncio.Semaphore(CONCURRENCY)
        page1 = await _fetch_page(session, sem, 1)
        total = _total_pages(page1)
        print(f"[peloton] total_pages={total}")

        rest = await asyncio.gather(*[
            _fetch_page(session, sem, p) for p in range(2, total + 1)
        ])

    seen = set()
    jobs = []
    for html in [page1] + list(rest):
        for job in _parse_page(html):
            if job["role_id"] not in seen:
                seen.add(job["role_id"])
                jobs.append(job)

    print(f"[peloton] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["team"])

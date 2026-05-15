import asyncio
import re
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup

SEARCH_URL  = "https://apply.deloitte.com/en_US/careers/SearchJobs/"
PARAMS_BASE = {"jobSort": "relevancy", "jobRecordsPerPage": 10}
CONCURRENCY = 4


def _parse_page(html: str) -> tuple[list[dict], int]:
    soup  = BeautifulSoup(html, "html.parser")
    total = 0
    jobs  = []
    for art in soup.select("article.article--result"):
        if not total:
            try:
                total = int(art.get("data-total", 0))
            except ValueError:
                pass
        a        = art.select_one("h3.article__header__text__title a")
        spans    = art.select("div.article__header__text__subtitle span")
        if not a:
            continue
        href     = a["href"]
        job_id   = href.rstrip("/").split("/")[-1]
        title    = a.get_text(strip=True)
        location = spans[-1].get_text(strip=True) if spans else ""
        team     = spans[1].get_text(strip=True) if len(spans) >= 2 else ""
        jobs.append({
            "role_id":     f"deloitte_{job_id}",
            "title":       title,
            "team":        team,
            "location":    location,
            "posted_date": "",
            "url":         href,
            "company":     "Deloitte",
        })
    return jobs, total


async def _fetch(session: AsyncSession, sem: asyncio.Semaphore, offset: int) -> list[dict]:
    async with sem:
        for attempt in range(3):
            try:
                r = await session.get(
                    SEARCH_URL,
                    params={**PARAMS_BASE, "jobOffset": offset},
                    timeout=45,
                )
                r.raise_for_status()
                jobs, _ = _parse_page(r.text)
                return jobs
            except Exception:
                if attempt == 2:
                    raise
                await asyncio.sleep(2 ** attempt)
    return []


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        # First page to get total
        r0 = await session.get(SEARCH_URL, params={**PARAMS_BASE, "jobOffset": 0}, timeout=30)
        r0.raise_for_status()
        first_jobs, total = _parse_page(r0.text)
        print(f"[deloitte] total={total}")

        sem  = asyncio.Semaphore(CONCURRENCY)
        rest = await asyncio.gather(*[
            _fetch(session, sem, offset)
            for offset in range(10, total, 10)
        ])

    seen = set()
    jobs = []
    for batch in [first_jobs] + list(rest):
        for job in batch:
            if job["role_id"] not in seen:
                seen.add(job["role_id"])
                jobs.append(job)

    print(f"[deloitte] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["team"])

import asyncio
import re
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup

BASE_URL    = "https://careers.westinghousenuclear.com"
SEARCH_URL  = f"{BASE_URL}/go/All-Careers/8736400/"
LIMIT       = 25
CONCURRENCY = 4


def _parse_page(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    for row in soup.select("tr.data-row"):
        a = row.select_one("a.jobTitle-link")
        if not a:
            continue
        href   = a["href"]
        m      = re.search(r"/(\d+)/?$", href)
        job_id = m.group(1) if m else ""
        title  = a.get_text(strip=True)
        loc_el = row.select_one("td.colLocation span.jobLocation")
        date_el = row.select_one("td.colDate span.jobDate")
        if not job_id or not title:
            continue
        jobs.append({
            "role_id":     f"westinghouse_{job_id}",
            "title":       title,
            "team":        "",
            "location":    loc_el.get_text(strip=True) if loc_el else "",
            "posted_date": date_el.get_text(strip=True) if date_el else "",
            "url":         BASE_URL + href,
            "company":     "Westinghouse",
        })
    return jobs


async def _fetch(session: AsyncSession, sem: asyncio.Semaphore, offset: int) -> list[dict]:
    async with sem:
        for attempt in range(3):
            try:
                r = await session.get(f"{SEARCH_URL}{offset}/", timeout=60)
                r.raise_for_status()
                return _parse_page(r.text)
            except Exception:
                if attempt == 2:
                    raise
                await asyncio.sleep(2 ** attempt)
    return []


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        for attempt in range(4):
            try:
                r0 = await session.get(f"{SEARCH_URL}0/", timeout=60)
                r0.raise_for_status()
                break
            except Exception:
                if attempt == 3:
                    raise
                await asyncio.sleep(3 ** attempt)
        first = _parse_page(r0.text)
        m     = re.search(r"of\s*<b>(\d+)</b>", r0.text)
        total = int(m.group(1)) if m else 0
        print(f"[westinghouse] total={total}")

        sem  = asyncio.Semaphore(CONCURRENCY)
        rest = await asyncio.gather(*[
            _fetch(session, sem, offset)
            for offset in range(LIMIT, total, LIMIT)
        ])

    seen = set()
    jobs = []
    for batch in [first] + list(rest):
        for job in batch:
            if job["role_id"] not in seen:
                seen.add(job["role_id"])
                jobs.append(job)

    print(f"[westinghouse] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])

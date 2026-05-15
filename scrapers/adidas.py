import asyncio
import re
from datetime import datetime
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup

BASE_URL    = "https://careers.adidas-group.com"
SEARCH_URL  = f"{BASE_URL}/jobs"
LIMIT       = 20
CONCURRENCY = 8


def _fmt_date(s: str) -> str:
    try:
        return datetime.strptime(s.strip(), "%b %d %Y").strftime("%b %d, %Y")
    except Exception:
        return ""


def _parse_page(html: str) -> tuple[list[dict], int]:
    soup  = BeautifulSoup(html, "html.parser")
    total_el = soup.select_one("[data-count-to]")
    total = int(total_el["data-count-to"]) if total_el else 0
    jobs  = []
    for li in soup.select("li.job-list__job"):
        a = li.select_one("a.job-list__inner")
        if not a:
            continue
        href     = a["href"].split("?")[0]
        m        = re.search(r"/(\d+)/?$", href)
        job_id   = m.group(1) if m else ""
        title_el = li.select_one("h3.job-list__title")
        title    = title_el.get_text(strip=True) if title_el else ""
        facts_el = li.select_one("p.job-list__facts")
        facts    = [p.strip() for p in re.split(r"\|", facts_el.get_text(separator="|", strip=True))] if facts_el else []
        location = facts[0] if facts else ""
        team     = facts[1] if len(facts) > 1 else ""
        date_el  = li.select_one("span.number-and-date")
        date_raw = date_el.get_text(strip=True).split(" - ")[0].strip() if date_el else ""
        if not job_id or not title:
            continue
        jobs.append({
            "role_id":     f"adidas_{job_id}",
            "title":       title,
            "team":        team,
            "location":    location,
            "posted_date": _fmt_date(date_raw),
            "url":         href,
            "company":     "Adidas",
        })
    return jobs, total


async def _fetch(session: AsyncSession, sem: asyncio.Semaphore, offset: int) -> list[dict]:
    async with sem:
        for attempt in range(3):
            try:
                r = await session.get(
                    SEARCH_URL,
                    params={"location": "", "offset": offset, "keywords": "", "location_manual": ""},
                    timeout=30,
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
        r0 = await session.get(
            SEARCH_URL,
            params={"location": "", "offset": 0, "keywords": "", "location_manual": ""},
            timeout=30,
        )
        r0.raise_for_status()
        first, total = _parse_page(r0.text)
        print(f"[adidas] total={total}")

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

    print(f"[adidas] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])

import asyncio
import re
from datetime import datetime
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup

BASE_URL    = "https://www.dickssportinggoods.jobs"
JOBS_URL    = f"{BASE_URL}/jobs/"
CALC_URL    = f"{BASE_URL}/calc-results/"
CONCURRENCY = 6


def _fmt_date(s: str) -> str:
    try:
        return datetime.strptime(s.strip(), "%m/%d/%Y").strftime("%b %d, %Y")
    except Exception:
        return ""


def _parse_page(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    for li in soup.select("li.result"):
        job_id = li.get("id", "").replace("result-", "").strip()
        a = li.select_one("a[href]")
        if not a or not job_id:
            continue
        href = a["href"]
        title_el = li.select_one("div.Results__list__title h3 strong")
        title = title_el.get_text(strip=True) if title_el else ""
        loc_items = li.select("ul.Results__list__info li.list-inline-item")
        location = loc_items[0].get_text(strip=True) if loc_items else ""
        team_el = li.select_one("div.career-area h4")
        team = team_el.get_text(strip=True) if team_el else ""
        date_el = li.select_one("div.dateposted div.text-sm")
        posted_date = _fmt_date(date_el.get_text(strip=True)) if date_el else ""
        if not title or not job_id:
            continue
        jobs.append({
            "role_id":     f"dsg_{job_id}",
            "title":       title,
            "team":        team,
            "location":    location,
            "posted_date": posted_date,
            "url":         BASE_URL + href,
            "company":     "Dick's Sporting Goods",
        })
    return jobs


async def _fetch(session: AsyncSession, sem: asyncio.Semaphore, page: int) -> list[dict]:
    async with sem:
        for attempt in range(3):
            try:
                r = await session.get(
                    CALC_URL,
                    params={"mypage": page},
                    headers={"Referer": JOBS_URL},
                    timeout=30,
                )
                r.raise_for_status()
                return _parse_page(r.text)
            except Exception:
                if attempt == 2:
                    raise
                await asyncio.sleep(2 ** attempt)
    return []


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r0 = await session.get(JOBS_URL, timeout=30)
        r0.raise_for_status()
        m = re.search(r'numpages\s*=\s*["\']?(\d+)', r0.text)
        numpages = int(m.group(1)) if m else 88
        print(f"[dsg] numpages={numpages}")

        sem     = asyncio.Semaphore(CONCURRENCY)
        results = await asyncio.gather(*[
            _fetch(session, sem, page)
            for page in range(numpages)
        ])

    seen = set()
    jobs = []
    for batch in results:
        for job in batch:
            if job["role_id"] not in seen:
                seen.add(job["role_id"])
                jobs.append(job)

    print(f"[dsg] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])

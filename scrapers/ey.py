import asyncio
import re
from html import unescape
from curl_cffi.requests import AsyncSession

BASE_URL = "https://careers.ey.com"
SEARCH   = BASE_URL + "/ey/search/"
HEADERS  = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept":     "text/html,application/xhtml+xml,*/*;q=0.9",
}
PARAMS_BASE = {
    "createNewAlert": "false",
    "q":              "",
    "locationsearch": "Pittsburgh",
    "local":          "en_US",
}
PER_PAGE = 25

JOB_RE = re.compile(
    r'href="(/ey/job/[^"]+/(\d+)/)"[^>]*class="jobTitle-link"[^>]*>\s*([\s\S]*?)\s*</a>',
)
LOC_RE  = re.compile(r'class="jobLocation[^"]*"[^>]*>\s*([^<]+?)\s*</span>')
PAGE_RE = re.compile(r'Page\s+\d+\s+of\s+(\d+)')


def _parse(html: str) -> list[tuple]:
    jobs   = []
    chunks = re.split(r'<td class="colTitle"', html)
    for chunk in chunks[1:]:
        m = JOB_RE.search(chunk)
        if not m:
            continue
        href, job_id, raw_title = m.group(1), m.group(2), m.group(3)
        title = unescape(re.sub(r"<[^>]+>", "", raw_title)).strip()
        lm    = LOC_RE.search(chunk)
        loc   = unescape(lm.group(1)).strip() if lm else ""
        jobs.append((href, job_id, title, loc))
    return jobs


async def _fetch(session: AsyncSession, startrow: int, sem: asyncio.Semaphore) -> list[tuple]:
    async with sem:
        r = await session.get(SEARCH, params={**PARAMS_BASE, "startrow": startrow}, headers=HEADERS, timeout=30)
        if r.status_code != 200:
            return []
        return _parse(r.text)


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r0 = await session.get(SEARCH, params=PARAMS_BASE, headers=HEADERS, timeout=30)
        r0.raise_for_status()
        html0 = r0.text
        pm    = PAGE_RE.search(html0)
        total_pages = int(pm.group(1)) if pm else 1
        page1 = _parse(html0)
        print(f"[ey] total_pages={total_pages}")

        sem     = asyncio.Semaphore(4)
        offsets = [p * PER_PAGE for p in range(1, total_pages)]
        rest    = await asyncio.gather(*[_fetch(session, off, sem) for off in offsets])

    raw = page1 + [j for batch in rest for j in batch]

    seen: set[str] = set()
    jobs: list[dict] = []
    for href, job_id, title, loc in raw:
        if not job_id or not title or job_id in seen:
            continue
        seen.add(job_id)
        jobs.append({
            "role_id":     f"ey_{job_id}",
            "title":       title,
            "team":        "",
            "location":    loc,
            "posted_date": "",
            "url":         BASE_URL + href,
            "company":     "EY",
            "experience":  "",
        })

    print(f"[ey] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"])
    print(f"Total: {len(jobs)}")

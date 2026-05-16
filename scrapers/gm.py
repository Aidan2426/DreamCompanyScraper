import asyncio
import re
from curl_cffi.requests import AsyncSession

BASE    = "https://search-careers.gm.com"
SEARCH  = BASE + "/en/jobs/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept":     "text/html,application/xhtml+xml,*/*;q=0.9",
}

CARD_RE  = re.compile(r'class="card-job-actions js-job"\s+data-id="([^"]+)"\s+data-jobtitle="([^"]+)"')
HREF_RE  = re.compile(r'href="(/en/jobs/jr-[^"]+/)"')
BRIEF_RE = re.compile(r'#briefcase[^>]*></use></svg>\s*([^<\n]+)')
MAP_RE   = re.compile(r'#map-marker[^>]*></use></svg>\s*([^<\n]+)')
PAGE_RE  = re.compile(r'page=(\d+)')


def _parse_page(html: str) -> list[dict]:
    jobs = []
    chunks = re.split(r'class="card card-job js-animate"', html)
    for chunk in chunks[1:]:
        cm = CARD_RE.search(chunk)
        if not cm:
            continue
        job_id = cm.group(1).strip()
        title  = cm.group(2).strip()
        hm     = HREF_RE.search(chunk)
        url    = BASE + hm.group(1) if hm else ""
        bm     = BRIEF_RE.search(chunk)
        team   = bm.group(1).strip() if bm else ""
        mm     = MAP_RE.search(chunk)
        loc    = mm.group(1).strip() if mm else ""
        jobs.append({
            "role_id":     f"gm_{job_id}",
            "title":       title,
            "team":        team,
            "location":    loc,
            "posted_date": "",
            "url":         url,
            "company":     "General Motors",
            "experience":  "",
        })
    return jobs


def _last_page(html: str) -> int:
    pages = [int(m) for m in PAGE_RE.findall(html)]
    return max(pages) if pages else 1


async def _fetch(session: AsyncSession, page: int, sem: asyncio.Semaphore) -> list[dict]:
    async with sem:
        r = await session.get(SEARCH, params={"search": "", "location": "", "page": page},
                              headers=HEADERS, timeout=30)
        if r.status_code != 200:
            return []
        return _parse_page(r.text)


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r0 = await session.get(SEARCH, params={"search": "", "location": ""},
                               headers=HEADERS, timeout=30)
        r0.raise_for_status()
        total_pages = _last_page(r0.text)
        page1 = _parse_page(r0.text)
        print(f"[gm] total_pages={total_pages}")

        sem  = asyncio.Semaphore(6)
        rest = await asyncio.gather(*[_fetch(session, p, sem) for p in range(2, total_pages + 1)])

    raw = page1 + [j for batch in rest for j in batch]

    seen: set[str] = set()
    jobs: list[dict] = []
    for j in raw:
        if not j["role_id"] or j["role_id"] in seen:
            continue
        seen.add(j["role_id"])
        jobs.append(j)

    print(f"[gm] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["team"])
    print(f"Total: {len(jobs)}")

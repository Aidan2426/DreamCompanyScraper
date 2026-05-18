import asyncio
import re
from curl_cffi.requests import AsyncSession

BASE     = "https://bloomberg.avature.net"
SEARCH   = BASE + "/careers/SearchJobs/"
HEADERS  = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept":     "text/html,application/xhtml+xml,*/*;q=0.9",
}
PER_PAGE = 12

TOTAL_RE = re.compile(r'(\d+)\s+results?', re.IGNORECASE)
JOB_RE   = re.compile(
    r'<a class="link" href="(https?://bloomberg\.avature\.net/careers/JobDetail/[^"]+/(\d+))"[^>]*>\s*([^<]+?)\s*</a>'
    r'.*?<span class="list-item-location">([^<]*)</span>',
    re.DOTALL,
)


def _parse(html: str) -> list[dict]:
    jobs = []
    for m in JOB_RE.finditer(html):
        url    = m.group(1).strip()
        job_id = m.group(2).strip()
        title  = re.sub(r'\s+', ' ', m.group(3)).strip()
        loc    = re.sub(r'\s+', ' ', m.group(4)).strip()
        if not job_id or not title:
            continue
        jobs.append({
            "role_id":     f"bloomberg_{job_id}",
            "title":       title,
            "team":        "",
            "location":    loc,
            "posted_date": "",
            "url":         url,
            "company":     "Bloomberg",
            "experience":  "",
        })
    return jobs


async def _fetch(session: AsyncSession, offset: int, sem: asyncio.Semaphore) -> list[dict]:
    async with sem:
        r = await session.get(
            SEARCH,
            params={"jobRecordsPerPage": PER_PAGE, "jobOffset": offset},
            headers=HEADERS,
            timeout=30,
        )
        if r.status_code != 200:
            return []
        return _parse(r.text)


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r0 = await session.get(
            SEARCH,
            params={"jobRecordsPerPage": PER_PAGE, "jobOffset": 0},
            headers=HEADERS,
            timeout=30,
        )
        r0.raise_for_status()
        page1 = _parse(r0.text)
        m     = TOTAL_RE.search(r0.text)
        total = int(m.group(1)) if m else PER_PAGE
        print(f"[bloomberg] total={total}")

        sem     = asyncio.Semaphore(4)
        offsets = range(PER_PAGE, total, PER_PAGE)
        rest    = await asyncio.gather(*[_fetch(session, off, sem) for off in offsets])

    raw = page1 + [j for batch in rest for j in batch]

    seen: set[str] = set()
    jobs: list[dict] = []
    for j in raw:
        if not j["role_id"] or j["role_id"] in seen:
            continue
        seen.add(j["role_id"])
        jobs.append(j)

    print(f"[bloomberg] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"])
    print(f"Total: {len(jobs)}")

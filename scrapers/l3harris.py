import asyncio
import re
import html as html_mod
from curl_cffi.requests import AsyncSession

BASE    = "https://careers.l3harris.com"
SEARCH  = BASE + "/en/search-jobs"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept":     "text/html,application/xhtml+xml,*/*;q=0.9",
}

PAGES_RE = re.compile(r'page\s+\d+\s+of\s+(\d+)', re.IGNORECASE)
JOB_RE   = re.compile(
    r'href="(/en/job/[^"]+/4832/(\d+))"[^>]+data-job-id="[^"]*"[^>]*>'
    r'.*?<h2[^>]*>\s*([^<]+?)\s*</h2>'
    r'.*?class="[^"]*job-category[^"]*">([^<]*)</span>'
    r'.*?class="[^"]*job-location[^"]*">([^<]*)</span>',
    re.DOTALL,
)


def _parse(html: str) -> list[dict]:
    jobs = []
    for m in JOB_RE.finditer(html):
        path   = m.group(1).strip()
        job_id = m.group(2).strip()
        title  = re.sub(r'\s+', ' ', html_mod.unescape(m.group(3))).strip()
        team   = re.sub(r'\s+', ' ', html_mod.unescape(re.sub(r'[|]+', ' ', m.group(4)))).strip()
        loc    = re.sub(r'\s+', ' ', html_mod.unescape(m.group(5))).strip()
        if not job_id or not title:
            continue
        jobs.append({
            "role_id":     f"l3harris_{job_id}",
            "title":       title,
            "team":        team,
            "location":    loc,
            "posted_date": "",
            "url":         BASE + path,
            "company":     "L3Harris",
            "experience":  "",
        })
    return jobs


async def _fetch(session: AsyncSession, page: int, sem: asyncio.Semaphore) -> list[dict]:
    async with sem:
        r = await session.get(SEARCH, params={"p": page}, headers=HEADERS, timeout=30)
        if r.status_code != 200:
            return []
        return _parse(r.text)


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r0 = await session.get(SEARCH, params={"p": 1}, headers=HEADERS, timeout=30)
        r0.raise_for_status()
        page1       = _parse(r0.text)
        m           = PAGES_RE.search(r0.text)
        total_pages = int(m.group(1)) if m else 1
        print(f"[l3harris] total_pages={total_pages}")

        sem  = asyncio.Semaphore(5)
        rest = await asyncio.gather(*[_fetch(session, p, sem) for p in range(2, total_pages + 1)])

    raw = page1 + [j for batch in rest for j in batch]

    seen: set[str] = set()
    jobs: list[dict] = []
    for j in raw:
        if not j["role_id"] or j["role_id"] in seen:
            continue
        seen.add(j["role_id"])
        jobs.append(j)

    print(f"[l3harris] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["team"])
    print(f"Total: {len(jobs)}")

import asyncio
import re
import html as html_mod
from curl_cffi.requests import AsyncSession

BASE    = "https://jobs.paloaltonetworks.com"
SEARCH  = BASE + "/en/search-jobs"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept":     "text/html,application/xhtml+xml,*/*;q=0.9",
}

PAGES_RE     = re.compile(r'page\s+\d+\s*/\s*(\d+)', re.IGNORECASE)
JOB_BLOCK_RE = re.compile(
    r'<a\b[^>]*href="(/en/job/[^"]+/47263/(\d+))"[^>]*>(.*?)</a>',
    re.DOTALL,
)
TITLE_RE = re.compile(r'<h[23][^>]*>\s*([^<]+?)\s*</h[23]>', re.DOTALL)
P_RE     = re.compile(r'<p[^>]*>\s*([^<]+?)\s*</p>', re.DOTALL)

# Known country names to split "Location Country Department" → (location, dept)
_COUNTRY_RE = re.compile(
    r'^(.*?(?:United States|United Kingdom|India|Israel|Canada|Australia|'
    r'Germany|Japan|Singapore|Mexico|Brazil|France|Netherlands|Sweden|'
    r'Switzerland|Ireland|Romania|Poland|Italy|Spain|Taiwan|South Korea|'
    r'Czech Republic|Hong Kong|Netherlands))\s+(.+)$',
    re.IGNORECASE,
)


def _split_loc_dept(text: str) -> tuple[str, str]:
    m = _COUNTRY_RE.match(text.strip())
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return text.strip(), ""


def _parse(html: str) -> list[dict]:
    jobs = []
    for m in JOB_BLOCK_RE.finditer(html):
        path    = m.group(1).strip()
        job_id  = m.group(2).strip()
        block   = m.group(3)

        tm = TITLE_RE.search(block)
        if not tm:
            continue
        title = re.sub(r'\s+', ' ', html_mod.unescape(tm.group(1))).strip()

        pm = P_RE.search(block)
        raw_p = re.sub(r'\s+', ' ', html_mod.unescape(pm.group(1))).strip() if pm else ""
        loc, team = _split_loc_dept(raw_p)

        if not job_id or not title:
            continue
        jobs.append({
            "role_id":     f"paloalto_{job_id}",
            "title":       title,
            "team":        team,
            "location":    loc,
            "posted_date": "",
            "url":         BASE + path,
            "company":     "Palo Alto Networks",
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
        print(f"[paloalto] total_pages={total_pages}")

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

    print(f"[paloalto] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["team"])
    print(f"Total: {len(jobs)}")

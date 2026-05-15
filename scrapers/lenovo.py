import asyncio
import re
from datetime import datetime
from curl_cffi.requests import AsyncSession

BASE     = "https://jobs.lenovo.com"
LIST_URL = BASE + "/en_US/careers/SearchJobs/"
HEADERS  = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36",
    "Accept":     "text/html,application/xhtml+xml,*/*",
}
PER_PAGE = 10


def _fmt_date(s: str) -> str:
    s = s.replace("Posted", "").strip()
    for fmt in ("%d-%b-%Y", "%B %d, %Y"):
        try:
            return datetime.strptime(s, fmt).strftime("%b %d, %Y")
        except Exception:
            pass
    return ""


def _parse_jobs(html: str) -> list[dict]:
    jobs = []
    for block in re.split(r'<article\s+class="article\s+article--result">', html)[1:]:
        m_link = re.search(r'href="(https://jobs\.lenovo\.com/en_US/careers/JobDetail/[^/]+/(\d+))"', block)
        m_title = re.search(r'class="article__header__text__title[^"]*">\s*<a[^>]*>\s*([^<]+?)\s*</a>', block, re.DOTALL)
        m_loc = re.search(r'article__header__text__subtitle.*?<span>\s*([^<]+?)\s*</span>', block, re.DOTALL)
        m_date = re.search(r'Posted\s+([\d]+-[A-Za-z]+-\d{4})', block)
        if not m_link or not m_title:
            continue
        jobs.append({
            "url":      m_link.group(1),
            "job_id":   m_link.group(2),
            "title":    m_title.group(1).strip(),
            "location": m_loc.group(1).strip() if m_loc else "",
            "date":     _fmt_date(m_date.group(0)) if m_date else "",
        })
    return jobs


async def _fetch(session: AsyncSession, offset: int) -> list[dict]:
    r = await session.get(
        LIST_URL,
        params={"listFilterMode": 1, "jobRecordsPerPage": PER_PAGE, "offset": offset},
        headers=HEADERS,
        timeout=30,
    )
    if r.status_code != 200:
        return []
    return _parse_jobs(r.text)


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r0 = await session.get(
            LIST_URL,
            params={"listFilterMode": 1, "jobRecordsPerPage": PER_PAGE, "offset": 0},
            headers=HEADERS,
            timeout=30,
        )
        r0.raise_for_status()
        m_total = re.search(r"of\s+(\d+)\s+jobs", r0.text, re.I)
        total = int(m_total.group(1)) if m_total else 0
        print(f"[lenovo] total={total}")
        page1 = _parse_jobs(r0.text)

        sem = asyncio.Semaphore(8)

        async def _guarded(offset):
            async with sem:
                return await _fetch(session, offset)

        rest = await asyncio.gather(*[_guarded(off) for off in range(PER_PAGE, total + PER_PAGE, PER_PAGE)])

    seen = set()
    jobs = []
    for j in page1 + [j for page in rest for j in page]:
        if j["job_id"] in seen:
            continue
        seen.add(j["job_id"])
        jobs.append({
            "role_id":     f"lenovo_{j['job_id']}",
            "title":       j["title"],
            "team":        "",
            "location":    j["location"],
            "posted_date": j["date"],
            "url":         j["url"],
            "company":     "Lenovo",
            "experience":  "",
        })

    print(f"[lenovo] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")

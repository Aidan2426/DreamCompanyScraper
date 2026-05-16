import asyncio
import math
import re
from datetime import datetime
from curl_cffi.requests import AsyncSession

BASE     = "https://www.lockheedmartinjobs.com"
LIST_URL = BASE + "/search-jobs"
HEADERS  = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36",
    "Accept":     "text/html,application/xhtml+xml,*/*",
}
PER_PAGE = 15


def _fmt_date(s: str) -> str:
    s = s.strip()
    try:
        return datetime.strptime(s, "%m/%d/%Y").strftime("%b %d, %Y")
    except Exception:
        return ""


def _parse_jobs(html: str) -> list[dict]:
    idx = html.find("results</p>")
    if idx == -1:
        idx = 0
    section = html[idx:]
    jobs = []
    for m in re.finditer(r'href="(/job/[^"]+/694/(\d+))"', section):
        url_path = m.group(1)
        job_id   = m.group(2)
        after    = section[m.end():m.end() + 600]
        m_title  = re.search(r'<span class="job-title">([^<]+)</span>', after)
        m_loc    = re.search(r'<span class="job-location">([^<]+)</span>', after)
        m_date   = re.search(r'<span class="job-date-posted">Date Posted:\s*([^<]+)</span>', after)
        if not m_title:
            continue
        jobs.append({
            "job_id":   job_id,
            "title":    m_title.group(1).strip(),
            "location": m_loc.group(1).strip() if m_loc else "",
            "date":     _fmt_date(m_date.group(1)) if m_date else "",
            "url":      BASE + url_path,
        })
    return jobs


async def _fetch(session: AsyncSession, page: int) -> list[dict]:
    r = await session.get(LIST_URL, params={"p": page}, headers=HEADERS, timeout=30)
    if r.status_code != 200:
        return []
    return _parse_jobs(r.text)


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r0 = await session.get(LIST_URL, params={"p": 1}, headers=HEADERS, timeout=30)
        r0.raise_for_status()
        m_total = re.search(r"([\d,]+)\s+results", r0.text)
        total   = int(m_total.group(1).replace(",", "")) if m_total else 0
        print(f"[lockheed] total={total}")
        page1 = _parse_jobs(r0.text)
        pages = math.ceil(total / PER_PAGE)

        sem = asyncio.Semaphore(10)

        async def _guarded(page):
            async with sem:
                return await _fetch(session, page)

        rest = await asyncio.gather(*[_guarded(p) for p in range(2, pages + 1)])

    seen = set()
    jobs = []
    for j in page1 + [j for page in rest for j in page]:
        if j["job_id"] in seen:
            continue
        seen.add(j["job_id"])
        jobs.append({
            "role_id":     f"lockheed_{j['job_id']}",
            "title":       j["title"],
            "team":        "",
            "location":    j["location"],
            "posted_date": j["date"],
            "url":         j["url"],
            "company":     "Lockheed Martin",
            "experience":  "",
        })

    print(f"[lockheed] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")

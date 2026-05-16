import asyncio
import re
from datetime import datetime
from curl_cffi.requests import AsyncSession

BASE     = "https://jobs.boeing.com"
LIST_URL = BASE + "/search-jobs"
HEADERS  = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36",
    "Accept":     "text/html,application/xhtml+xml,*/*",
}


def _fmt_date(s: str) -> str:
    try:
        return datetime.strptime(s.strip(), "%m/%d/%Y").strftime("%b %d, %Y")
    except Exception:
        return ""


def _parse_jobs(html: str) -> list[dict]:
    jobs = []
    # Split on job links
    chunks = re.split(r'(?=href="/job/[^"]+/\d+"[^>]*data-job-id="\d+")', html)
    for chunk in chunks[1:]:
        m_link = re.match(r'href="(/job/[^"]+/(\d+))"', chunk)
        if not m_link:
            continue
        path, job_id = m_link.group(1), m_link.group(2)
        m_title = re.search(r'search-results__job-title">([^<]+)<', chunk)
        m_loc   = re.search(r'search-results__job-info location">([^<]+)<', chunk)
        m_date  = re.search(r'search-results__job-info date">([^<]+)<', chunk)
        title   = m_title.group(1).strip() if m_title else ""
        if not title:
            continue
        jobs.append({
            "path":     path,
            "job_id":   job_id,
            "title":    title,
            "location": m_loc.group(1).strip() if m_loc else "",
            "date":     _fmt_date(m_date.group(1)) if m_date else "",
        })
    return jobs


async def _fetch_page(session: AsyncSession, page: int) -> list[dict]:
    r = await session.get(LIST_URL, params={"p": page}, headers=HEADERS, timeout=30)
    if r.status_code != 200:
        return []
    return _parse_jobs(r.text)


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r0 = await session.get(LIST_URL, params={"p": 1}, headers=HEADERS, timeout=30)
        r0.raise_for_status()
        html0 = r0.text

        total_pages_m = re.search(r'data-total-pages="(\d+)"', html0)
        total_pages   = int(total_pages_m.group(1)) if total_pages_m else 1
        total_m       = re.search(r'data-total-results="(\d+)"', html0)
        total         = total_m.group(1) if total_m else "?"
        print(f"[boeing] total={total} pages={total_pages}")

        page1_jobs = _parse_jobs(html0)

        sem = asyncio.Semaphore(10)

        async def _guarded(page):
            async with sem:
                return await _fetch_page(session, page)

        rest = await asyncio.gather(*[_guarded(p) for p in range(2, total_pages + 1)])

    seen = set()
    jobs = []
    for j in page1_jobs + [j for page in rest for j in page]:
        if j["job_id"] in seen:
            continue
        seen.add(j["job_id"])
        jobs.append({
            "role_id":     f"boeing_{j['job_id']}",
            "title":       j["title"],
            "team":        "",
            "location":    j["location"],
            "posted_date": j["date"],
            "url":         BASE + j["path"],
            "company":     "Boeing",
            "experience":  "",
        })

    print(f"[boeing] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")

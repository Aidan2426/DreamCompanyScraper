import asyncio
import math
import re
from curl_cffi.requests import AsyncSession

BASE     = "https://jobs.kennametal.com"
LIST_URL = BASE + "/search/"
HEADERS  = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36",
    "Accept":     "text/html,application/xhtml+xml,*/*",
}
PER_PAGE = 25


def _parse_jobs(html: str) -> list[dict]:
    jobs = []
    seen = set()
    for chunk in re.split(r'<li class="job-tile job-id-', html)[1:]:
        m_id = re.match(r'(\d+)', chunk)
        if not m_id:
            continue
        job_id = m_id.group(1)
        if job_id in seen:
            continue
        seen.add(job_id)

        m_title = re.search(r'class="jobTitle-link[^"]*"[^>]*>\s*([^<]+)\s*<', chunk)
        title   = m_title.group(1).strip() if m_title else ""
        if not title:
            continue

        m_href  = re.search(r'href="(/job/[^"]+)"', chunk)
        path    = m_href.group(1) if m_href else f"/job/{job_id}/"

        m_loc   = re.search(rf'id="job-{job_id}-desktop-section-location-value"[^>]*>\s*([^<]+)', chunk)
        location = m_loc.group(1).strip() if m_loc else ""

        m_date  = re.search(rf'id="job-{job_id}-desktop-section-date-value"[^>]*>\s*([^<]+)', chunk)
        date    = m_date.group(1).strip() if m_date else ""

        jobs.append({
            "job_id":   job_id,
            "title":    title,
            "location": location,
            "date":     date,
            "url":      BASE + path,
        })
    return jobs


async def _fetch(session: AsyncSession, startrow: int) -> list[dict]:
    r = await session.get(
        LIST_URL,
        params={"q": "", "locationsearch": "", "startrow": startrow},
        headers=HEADERS,
        timeout=60,
    )
    if r.status_code != 200:
        return []
    return _parse_jobs(r.text)


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r0 = await session.get(
            LIST_URL,
            params={"q": "", "locationsearch": "", "startrow": 1},
            headers=HEADERS,
            timeout=30,
        )
        r0.raise_for_status()
        html0   = r0.text
        m_total = re.search(r"Showing \d+ to \d+ of ([\d,]+)", html0)
        total   = int(m_total.group(1).replace(",", "")) if m_total else 0
        print(f"[kennametal] total={total}")
        page1   = _parse_jobs(html0)

        offsets = list(range(PER_PAGE + 1, total + 1, PER_PAGE))
        rest = []
        for off in offsets:
            rest.append(await _fetch(session, off))

    seen = set()
    jobs = []
    for j in page1 + [j for page in rest for j in page]:
        if j["job_id"] in seen:
            continue
        seen.add(j["job_id"])
        jobs.append({
            "role_id":     f"kennametal_{j['job_id']}",
            "title":       j["title"],
            "team":        "",
            "location":    j["location"],
            "posted_date": j["date"],
            "url":         j["url"],
            "company":     "Kennametal",
            "experience":  "",
        })

    print(f"[kennametal] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")

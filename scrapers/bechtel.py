import asyncio
import math
import re
from html import unescape
from curl_cffi.requests import AsyncSession

BASE     = "https://jobs.bechtel.com"
LIST_URL = BASE + "/go/Professional/4321400"
HEADERS  = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36",
    "Accept":     "text/html,application/xhtml+xml,*/*",
}
PER_PAGE = 25


def _parse_jobs(html: str) -> list[dict]:
    jobs = []
    for chunk in html.split('<tr class="data-row">')[1:]:
        m_href = re.search(r'class="jobTitle-link"\s+href="([^"]+)"|href="([^"]+)"\s+class="jobTitle-link"', chunk)
        if not m_href:
            continue
        path   = (m_href.group(1) or m_href.group(2)).strip()
        m_id   = re.search(r'/(\d+)/?$', path)
        job_id = m_id.group(1) if m_id else ""
        m_title = re.search(r'class="jobTitle-link"[^>]*>([^<]+)<', chunk)
        title   = unescape(m_title.group(1).strip()) if m_title else ""
        if not job_id or not title:
            continue

        # location from desktop column (first jobLocation after colLocation)
        m_loc  = re.search(r'colLocation[^>]*>.*?<span class="jobLocation">([^<]+)', chunk, re.DOTALL)
        if not m_loc:
            m_loc = re.search(r'<span class="jobLocation">([^<]+)', chunk)
        location = m_loc.group(1).strip() if m_loc else ""
        # strip postal code at end: "City, ST, US, 12345" → "City, ST, US"
        location = re.sub(r',\s*\d{4,6}\s*$', '', location).strip()

        m_dept = re.search(r'class="jobFacility[^"]*">([^<]+)', chunk)
        dept   = re.sub(r'\s+', ' ', unescape(m_dept.group(1).strip())) if m_dept else ""

        jobs.append({
            "job_id":   job_id,
            "title":    title,
            "location": location,
            "dept":     dept,
            "url":      BASE + path,
        })
    return jobs


async def _fetch(session: AsyncSession, offset: int, sem: asyncio.Semaphore) -> list[dict]:
    async with sem:
        url = f"{LIST_URL}/{offset}/" if offset > 0 else f"{LIST_URL}/"
        r = await session.get(
            url,
            params={"q": "", "sortColumn": "referencedate", "sortDirection": "desc"},
            headers=HEADERS,
            timeout=60,
        )
        if r.status_code != 200:
            return []
        return _parse_jobs(r.text)


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r0 = await session.get(
            f"{LIST_URL}/",
            params={"q": "", "sortColumn": "referencedate", "sortDirection": "desc"},
            headers=HEADERS,
            timeout=60,
        )
        r0.raise_for_status()
        html0   = r0.text
        m_total = re.search(r"Results \d+ to \d+ of ([\d,]+)", html0, re.IGNORECASE)
        total   = int(m_total.group(1).replace(",", "")) if m_total else 712
        print(f"[bechtel] total={total}")
        page1   = _parse_jobs(html0)

        sem     = asyncio.Semaphore(6)
        offsets = list(range(PER_PAGE, total + PER_PAGE, PER_PAGE))
        rest    = await asyncio.gather(*[_fetch(session, off, sem) for off in offsets])

    seen = set()
    jobs = []
    for j in page1 + [j for page in rest for j in page]:
        if j["job_id"] in seen:
            continue
        seen.add(j["job_id"])
        jobs.append({
            "role_id":     f"bechtel_{j['job_id']}",
            "title":       j["title"],
            "team":        j["dept"],
            "location":    j["location"],
            "posted_date": "",
            "url":         j["url"],
            "company":     "Bechtel",
            "experience":  "",
        })

    print(f"[bechtel] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["team"])
    print(f"Total: {len(jobs)}")

import asyncio
import math
import re
from curl_cffi.requests import AsyncSession

BASE     = "https://careers.servicenow.com"
LIST_URL = BASE + "/jobs/"
HEADERS  = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept":     "text/html,application/xhtml+xml,*/*;q=0.9",
}
PER_PAGE = 20


def _parse_jobs(html: str) -> list[dict]:
    jobs = []
    for chunk in html.split('<div class="card card-job">')[1:]:
        m_href  = re.search(r'href="(/jobs/(\d+)/[^"]*)"', chunk)
        if not m_href:
            continue
        path   = m_href.group(1)
        job_id = m_href.group(2)

        m_title = re.search(r'class="stretched-link js-view-job"[^>]*>([^<]+)<', chunk)
        title   = m_title.group(1).strip() if m_title else ""
        if not title:
            title_attr = re.search(r'data-jobtitle="([^"]+)"', chunk)
            title = title_attr.group(1).strip() if title_attr else ""
        if not title:
            continue

        m_loc  = re.search(r'#map-marker"></use></svg>\s*([^\n<]+)', chunk)
        location = m_loc.group(1).strip() if m_loc else ""

        jobs.append({
            "job_id":   job_id,
            "title":    title,
            "location": location,
            "url":      BASE + path,
        })
    return jobs


async def _fetch(session: AsyncSession, page: int, sem: asyncio.Semaphore) -> list[dict]:
    async with sem:
        r = await session.get(
            LIST_URL,
            params={"search": "", "origin": "global", "page": page},
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
            params={"search": "", "origin": "global", "page": 1},
            headers=HEADERS,
            timeout=30,
        )
        r0.raise_for_status()
        html0   = r0.text
        m_total = re.search(r'data-results="(\d+)"', html0)
        total   = int(m_total.group(1)) if m_total else 0
        print(f"[servicenow] total={total}")
        page1   = _parse_jobs(html0)
        pages   = math.ceil(total / PER_PAGE)

        sem  = asyncio.Semaphore(6)
        rest = await asyncio.gather(*[_fetch(session, p, sem) for p in range(2, pages + 1)])

    seen = set()
    jobs = []
    for j in page1 + [j for page in rest for j in page]:
        if j["job_id"] in seen:
            continue
        seen.add(j["job_id"])
        jobs.append({
            "role_id":     f"servicenow_{j['job_id']}",
            "title":       j["title"],
            "team":        "",
            "location":    j["location"],
            "posted_date": "",
            "url":         j["url"],
            "company":     "ServiceNow",
            "experience":  "",
        })

    print(f"[servicenow] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"])
    print(f"Total: {len(jobs)}")

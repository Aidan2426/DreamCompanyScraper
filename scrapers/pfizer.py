import asyncio
import re
from curl_cffi.requests import AsyncSession

API_URL  = "https://pfizer.wd1.myworkdayjobs.com/wday/cxs/pfizer/PfizerCareers/jobs"
JOB_BASE = "https://pfizer.wd1.myworkdayjobs.com/en-US/PfizerCareers"
HEADERS  = {
    "User-Agent":   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept":       "application/json",
    "Content-Type": "application/json",
}
PER_PAGE = 20


def _parse_posted(s: str) -> str:
    if not s:
        return ""
    s = s.strip()
    if "Today" in s:
        from datetime import date
        return date.today().strftime("%b %d, %Y")
    m = re.search(r"(\d+)\s+Day", s)
    if m:
        from datetime import date, timedelta
        d = date.today() - timedelta(days=int(m.group(1)))
        return d.strftime("%b %d, %Y")
    return ""


async def _fetch(session: AsyncSession, offset: int, sem: asyncio.Semaphore) -> list[dict]:
    async with sem:
        r = await session.post(
            API_URL,
            json={"limit": PER_PAGE, "offset": offset, "searchText": "", "locations": []},
            headers=HEADERS,
            timeout=30,
        )
        if r.status_code != 200:
            return []
        return r.json().get("jobPostings", [])


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r0 = await session.post(
            API_URL,
            json={"limit": PER_PAGE, "offset": 0, "searchText": "", "locations": []},
            headers=HEADERS,
            timeout=30,
        )
        r0.raise_for_status()
        data0 = r0.json()
        total = data0.get("total", 0)
        page1 = data0.get("jobPostings", [])
        print(f"[pfizer] total={total}")

        sem     = asyncio.Semaphore(6)
        offsets = range(PER_PAGE, total, PER_PAGE)
        rest    = await asyncio.gather(*[_fetch(session, off, sem) for off in offsets])

    raw = page1 + [j for batch in rest for j in batch]

    seen: set[str] = set()
    jobs: list[dict] = []
    for j in raw:
        path   = j.get("externalPath", "")
        job_id = path.rsplit("/", 1)[-1].strip() if path else ""
        title  = (j.get("title") or "").strip()
        if not job_id or not title or job_id in seen:
            continue
        seen.add(job_id)
        jobs.append({
            "role_id":     f"pfizer_{job_id}",
            "title":       title,
            "team":        "",
            "location":    (j.get("locationsText") or "").strip(),
            "posted_date": _parse_posted(j.get("postedOn") or ""),
            "url":         JOB_BASE + path if path else "",
            "company":     "Pfizer",
            "experience":  "",
        })

    print(f"[pfizer] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")

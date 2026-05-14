import asyncio
from curl_cffi.requests import AsyncSession

BASE_URL  = "https://mycareer.verizon.com/api/jobs/search"
SEED_URL  = "https://mycareer.verizon.com/jobs/"
JOB_BASE  = "https://mycareer.verizon.com"
CONCURRENCY = 5
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://mycareer.verizon.com/jobs/",
    "Origin": "https://mycareer.verizon.com",
}


def _parse_location(locs: list) -> str:
    if not locs:
        return ""
    loc = locs[0]
    city   = loc.get("City") or ""
    region = loc.get("Region") or ""
    if city and region:
        return f"{city}, {region}"
    return city or region or loc.get("Identifier") or ""


def _parse_url(urls: list) -> str:
    for u in urls or []:
        if u.get("IsDefault"):
            return JOB_BASE + u["Url"]
    if urls:
        return JOB_BASE + urls[0].get("Url", "")
    return ""


async def _fetch_page(session: AsyncSession, sem: asyncio.Semaphore, page: int) -> list[dict]:
    async with sem:
        try:
            r = await session.get(BASE_URL, params={"page": page}, headers=HEADERS)
            r.raise_for_status()
            return r.json().get("jobs", [])
        except Exception:
            return []


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        await session.get(SEED_URL)
        r = await session.get(BASE_URL, params={"page": 1}, headers=HEADERS)
        r.raise_for_status()
        data = r.json()
        total_pages = data.get("totalPages", 114)
        first_jobs  = data.get("jobs", [])
        print(f"[verizon] {data.get('totalJobs', '?')} jobs across {total_pages} pages")

        sem = asyncio.Semaphore(CONCURRENCY)
        rest = await asyncio.gather(*[_fetch_page(session, sem, p) for p in range(2, total_pages + 1)])

    raw = first_jobs + [job for page in rest for job in page]

    seen = set()
    jobs = []
    for j in raw:
        job_id = j.get("Id") or ""
        title  = (j.get("Title") or "").strip()
        if not job_id or not title or job_id in seen:
            continue
        seen.add(job_id)
        jobs.append({
            "role_id":     f"verizon_{job_id}",
            "title":       title,
            "team":        (j.get("Teams") or [""])[0],
            "location":    _parse_location(j.get("Locations")),
            "posted_date": "",
            "url":         _parse_url(j.get("Urls")),
            "company":     "Verizon",
        })

    print(f"[verizon] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j)

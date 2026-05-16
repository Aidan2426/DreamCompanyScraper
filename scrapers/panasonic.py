import asyncio
from datetime import datetime
from curl_cffi.requests import AsyncSession

API_URL  = "https://careers.na.panasonic.com/api/jobs"
JOB_BASE = "https://careers.na.panasonic.com/careers-home/jobs"
HEADERS  = {
    "Accept":  "application/json",
    "Referer": "https://careers.na.panasonic.com/careers-home/jobs",
}
LIMIT       = 100
CONCURRENCY = 5


def _fmt_date(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%b %d, %Y")
    except Exception:
        return ""


async def _fetch_page(session: AsyncSession, sem: asyncio.Semaphore, page: int) -> list[dict]:
    async with sem:
        r = await session.get(API_URL, params={"limit": LIMIT, "page": page},
                              headers=HEADERS, timeout=30)
        r.raise_for_status()
        return r.json().get("jobs", [])


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r0 = await session.get(API_URL, params={"limit": LIMIT, "page": 1},
                               headers=HEADERS, timeout=30)
        r0.raise_for_status()
        data0      = r0.json()
        total      = data0.get("totalCount", 0)
        first_jobs = data0.get("jobs", [])
        total_pages = (total + LIMIT - 1) // LIMIT
        print(f"[panasonic] total={total}, {total_pages} pages")

        sem  = asyncio.Semaphore(CONCURRENCY)
        rest = await asyncio.gather(*[
            _fetch_page(session, sem, p) for p in range(2, total_pages + 1)
        ])

    raw = first_jobs + [j for page in rest for j in page]

    seen = set()
    jobs = []
    for item in raw:
        j      = item.get("data", {})
        req_id = (j.get("req_id") or "").strip()
        title  = (j.get("title")  or "").strip()
        if not req_id or not title or req_id in seen:
            continue
        seen.add(req_id)

        cats = j.get("categories") or []
        team = cats[0].get("name", "") if cats else ""

        jobs.append({
            "role_id":     f"panasonic_{req_id}",
            "title":       title,
            "team":        team,
            "location":    (j.get("full_location") or "").strip(),
            "posted_date": _fmt_date(j.get("posted_date") or ""),
            "url":         f"{JOB_BASE}/{req_id}",
            "company":     "Panasonic",
        })

    print(f"[panasonic] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])

import asyncio
import math
from datetime import datetime
from curl_cffi.requests import AsyncSession

API_URL  = "https://careers.rivian.com/api/jobs"
JOB_BASE = "https://careers.rivian.com/careers-home/jobs"
HEADERS  = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept":     "application/json",
}
PER_PAGE = 50


def _fmt_date(s: str) -> str:
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").strftime("%b %d, %Y")
    except Exception:
        return ""


async def _fetch(session: AsyncSession, page: int, sem: asyncio.Semaphore) -> list[dict]:
    async with sem:
        r = await session.get(API_URL, params={"limit": PER_PAGE, "page": page},
                              headers=HEADERS, timeout=30)
        if r.status_code != 200:
            return []
        return r.json().get("jobs", [])


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r0 = await session.get(API_URL, params={"limit": PER_PAGE, "page": 1},
                               headers=HEADERS, timeout=30)
        r0.raise_for_status()
        data0       = r0.json()
        total       = data0.get("totalCount", 0)
        page1       = data0.get("jobs", [])
        total_pages = math.ceil(total / PER_PAGE)
        print(f"[rivian] total={total}, pages={total_pages}")

        sem  = asyncio.Semaphore(6)
        rest = await asyncio.gather(*[_fetch(session, p, sem) for p in range(2, total_pages + 1)])

    raw = page1 + [j for batch in rest for j in batch]

    seen: set[str] = set()
    jobs: list[dict] = []
    for entry in raw:
        d      = entry.get("data", {})
        req_id = (d.get("req_id") or "").strip()
        title  = (d.get("title") or "").strip()
        if not req_id or not title or req_id in seen:
            continue
        seen.add(req_id)
        slug = (d.get("slug") or req_id).strip()
        jobs.append({
            "role_id":     f"rivian_{req_id}",
            "title":       title,
            "team":        (d.get("department") or "").strip(),
            "location":    (d.get("location_name") or "").strip(),
            "posted_date": _fmt_date(d.get("posted_date") or ""),
            "url":         f"{JOB_BASE}/{slug}",
            "company":     "Rivian",
            "experience":  "",
        })

    print(f"[rivian] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")

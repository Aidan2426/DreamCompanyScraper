import asyncio
import math
from curl_cffi.requests import AsyncSession
from datetime import datetime, timezone

SEED_URL = "https://www.uber.com/us/en/careers/list/"
API_URL  = "https://www.uber.com/api/loadSearchJobsResults"
JOB_BASE = "https://www.uber.com/us/en/careers/list"
PAGE_SIZE   = 100
CONCURRENCY = 5

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Referer": SEED_URL,
    "Origin": "https://www.uber.com",
    "x-csrf-token": "x",
}


def _fmt_date(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%b %d, %Y")
    except Exception:
        return ""


def _location(loc: dict) -> str:
    if not loc:
        return ""
    city   = loc.get("city") or ""
    region = loc.get("region") or ""
    country = loc.get("countryName") or loc.get("country") or ""
    if city and region and country == "United States":
        return f"{city}, {region}"
    if city and country:
        return f"{city}, {country}"
    return city or region or country


async def _fetch_page(session: AsyncSession, sem: asyncio.Semaphore, page: int) -> list[dict]:
    async with sem:
        try:
            r = await session.post(API_URL,
                json={"limit": PAGE_SIZE, "page": page, "params": {}},
                headers=HEADERS, timeout=30)
            r.raise_for_status()
            return r.json().get("data", {}).get("results", [])
        except Exception:
            return []


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        await session.get(SEED_URL, timeout=15)

        r = await session.post(API_URL,
            json={"limit": PAGE_SIZE, "page": 0, "params": {}},
            headers=HEADERS, timeout=30)
        r.raise_for_status()
        data        = r.json().get("data", {})
        total       = (data.get("totalResults") or {}).get("low", 0)
        total_pages = math.ceil(total / PAGE_SIZE)
        first_raw   = data.get("results", [])
        print(f"[uber] {total} jobs across {total_pages} pages")

        sem  = asyncio.Semaphore(CONCURRENCY)
        rest = await asyncio.gather(*[_fetch_page(session, sem, p) for p in range(1, total_pages)])

    all_raw = first_raw + [j for page in rest for j in page]

    seen = set()
    jobs = []
    for j in all_raw:
        job_id = str(j.get("id") or "").strip()
        title  = (j.get("title") or "").strip()
        if not job_id or not title or job_id in seen:
            continue
        seen.add(job_id)
        jobs.append({
            "role_id":     f"uber_{job_id}",
            "title":       title,
            "team":        (j.get("department") or j.get("team") or "").strip(),
            "location":    _location(j.get("location")),
            "posted_date": _fmt_date(j.get("creationDate") or ""),
            "url":         f"{JOB_BASE}/{job_id}/",
            "company":     "Uber",
        })

    print(f"[uber] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print({k: v.encode("ascii", "replace").decode() for k, v in j.items()})

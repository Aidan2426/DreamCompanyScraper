import asyncio
from curl_cffi.requests import AsyncSession

BASE_URL    = "https://careers.nike.com"
JOBS_URL    = f"{BASE_URL}/jobs"
API_URL     = f"{BASE_URL}/api/get-jobs"
PAGE_SIZE   = 20
CONCURRENCY = 10


def _location(j: dict) -> str:
    locs = j.get("locations") or []
    if locs:
        return locs[0].get("cityState") or locs[0].get("city") or ""
    return ""


def _team(j: dict) -> str:
    for cf in j.get("customFields") or []:
        if cf.get("cfKey") == "cf_job_category":
            return cf.get("value") or ""
    return ""


async def _fetch(session: AsyncSession, sem: asyncio.Semaphore, page: int) -> list[dict]:
    async with sem:
        for attempt in range(3):
            try:
                r = await session.post(
                    API_URL,
                    params={"page_number": page, "page_size": PAGE_SIZE, "internal": "false"},
                    json={"site_available_languages": ["en"], "disable_switch_search_mode": False},
                    headers={"Referer": JOBS_URL},
                    timeout=30,
                )
                r.raise_for_status()
                return r.json().get("jobs", [])
            except Exception:
                if attempt == 2:
                    raise
                await asyncio.sleep(2 ** attempt)
    return []


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        await session.get(JOBS_URL, timeout=30)
        r0 = await session.post(
            API_URL,
            params={"page_number": 1, "page_size": PAGE_SIZE, "internal": "false"},
            json={"site_available_languages": ["en"], "disable_switch_search_mode": False},
            headers={"Referer": JOBS_URL},
            timeout=30,
        )
        r0.raise_for_status()
        d0    = r0.json()
        total = d0.get("totalJob", 0)
        first = d0.get("jobs", [])
        print(f"[nike] total={total}")

        import math
        num_pages = math.ceil(total / PAGE_SIZE)
        sem  = asyncio.Semaphore(CONCURRENCY)
        rest = await asyncio.gather(*[
            _fetch(session, sem, page)
            for page in range(2, num_pages + 1)
        ])

    seen = set()
    jobs = []
    for batch in [first] + list(rest):
        for j in batch:
            req_id = (j.get("requisitionID") or "").strip()
            title  = (j.get("title") or "").strip()
            if not req_id or not title or req_id in seen:
                continue
            seen.add(req_id)
            orig = (j.get("originalURL") or "").strip()
            jobs.append({
                "role_id":     f"nike_{req_id}",
                "title":       title,
                "team":        _team(j),
                "location":    _location(j),
                "posted_date": "",
                "url":         f"{JOBS_URL}/{orig}" if orig else "",
                "company":     "Nike",
            })

    print(f"[nike] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["team"])

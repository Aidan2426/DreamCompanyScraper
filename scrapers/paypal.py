import asyncio
import math
from datetime import datetime, timezone
from curl_cffi.requests import AsyncSession

DOMAIN   = "paypal.com"
SEARCH   = "https://paypal.eightfold.ai/api/pcsx/search"
JOB_BASE = "https://paypal.eightfold.ai"
HEADERS  = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36",
    "Accept":     "application/json",
    "Referer":    "https://paypal.eightfold.ai/careers",
}
PER_PAGE = 10


def _fmt_ts(ts) -> str:
    if not ts:
        return ""
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%b %d, %Y")
    except Exception:
        return ""


async def _fetch(session: AsyncSession, start: int) -> list[dict]:
    r = await session.get(
        SEARCH,
        params={"domain": DOMAIN, "query": "", "start": start, "num": PER_PAGE},
        headers=HEADERS,
        timeout=30,
    )
    if r.status_code != 200:
        return []
    return r.json().get("data", {}).get("positions", [])


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        await session.get("https://paypal.eightfold.ai/careers", timeout=30)

        r0 = await session.get(
            SEARCH,
            params={"domain": DOMAIN, "query": "", "start": 0, "num": PER_PAGE},
            headers=HEADERS,
            timeout=30,
        )
        r0.raise_for_status()
        d0    = r0.json().get("data", {})
        total = d0.get("count", 0)
        raw   = d0.get("positions", [])
        print(f"[paypal] total={total}")

        sem = asyncio.Semaphore(8)

        async def _guarded(start):
            async with sem:
                return await _fetch(session, start)

        pages = await asyncio.gather(*[_guarded(s) for s in range(PER_PAGE, total, PER_PAGE)])
        raw += [j for page in pages for j in page]

    seen = set()
    jobs = []
    for j in raw:
        job_id = str(j.get("id") or "").strip()
        title  = (j.get("name") or "").strip()
        if not job_id or not title or job_id in seen:
            continue
        seen.add(job_id)
        locs = j.get("locations") or []
        jobs.append({
            "role_id":     f"paypal_{job_id}",
            "title":       title,
            "team":        (j.get("department") or "").strip(),
            "location":    locs[0].strip() if locs else "",
            "posted_date": _fmt_ts(j.get("postedTs")),
            "url":         JOB_BASE + (j.get("positionUrl") or f"/careers/job/{job_id}"),
            "company":     "PayPal",
            "experience":  "",
        })

    print(f"[paypal] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["team"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")

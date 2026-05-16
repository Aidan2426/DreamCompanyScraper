import asyncio
import json
import math
import re
from datetime import datetime
from curl_cffi.requests import AsyncSession

LIST_URL = "https://careers.wbd.com/global/en/search-results"
JOB_BASE = "https://careers.wbd.com/global/en/job"
HEADERS  = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept":     "text/html,application/xhtml+xml,*/*;q=0.9",
}
PER_PAGE = 10


def _extract_ddo(html: str) -> dict:
    m = re.search(r'phApp\.ddo\s*=\s*', html)
    if not m:
        return {}
    start = m.end()
    depth = end = 0
    for i, c in enumerate(html[start:], start):
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    try:
        return json.loads(html[start:end])
    except Exception:
        return {}


def _fmt_date(s: str) -> str:
    if not s:
        return ""
    try:
        return datetime.fromisoformat(s.replace("+0000", "+00:00")).strftime("%b %d, %Y")
    except Exception:
        return ""


async def _fetch(session: AsyncSession, offset: int, sem: asyncio.Semaphore) -> list[dict]:
    async with sem:
        r = await session.get(LIST_URL, params={"from": offset}, headers=HEADERS, timeout=30)
        if r.status_code != 200:
            return []
        ddo = _extract_ddo(r.text)
        return ddo.get("eagerLoadRefineSearch", {}).get("data", {}).get("jobs", [])


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r0 = await session.get(LIST_URL, params={"from": 0}, headers=HEADERS, timeout=30)
        r0.raise_for_status()
        ddo0  = _extract_ddo(r0.text)
        total = ddo0.get("eagerLoadRefineSearch", {}).get("totalHits", 0)
        raw   = list(ddo0.get("eagerLoadRefineSearch", {}).get("data", {}).get("jobs", []))
        print(f"[wbd] total={total}")

        pages = math.ceil(total / PER_PAGE)
        sem   = asyncio.Semaphore(8)
        rest  = await asyncio.gather(*[_fetch(session, off, sem) for off in range(PER_PAGE, pages * PER_PAGE, PER_PAGE)])
        for batch in rest:
            raw.extend(batch)

    seen = set()
    jobs = []
    for j in raw:
        job_id = str(j.get("jobId") or j.get("reqId") or "").strip()
        title  = (j.get("title") or "").strip()
        if not job_id or not title or job_id in seen:
            continue
        seen.add(job_id)
        jobs.append({
            "role_id":     f"wbd_{job_id}",
            "title":       title,
            "team":        (j.get("category") or "").strip(),
            "location":    (j.get("cityStateCountry") or j.get("location") or "").strip(),
            "posted_date": _fmt_date(j.get("postedDate") or ""),
            "url":         f"{JOB_BASE}/{job_id}",
            "company":     "Warner Bros. Discovery",
            "experience":  "",
        })

    print(f"[wbd] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["team"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")

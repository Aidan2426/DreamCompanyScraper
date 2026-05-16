import asyncio
import math
from datetime import datetime
from curl_cffi.requests import AsyncSession

BASE     = "https://iawmqy.fa.ocs.oraclecloud.com"
API_URL  = BASE + "/hcmRestApi/resources/latest/recruitingCEJobRequisitions"
JOB_BASE = BASE + "/hcmUI/CandidateExperience/en/sites/careers/job"
HEADERS  = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36",
    "Accept":     "application/json",
    "Referer":    BASE + "/hcmUI/CandidateExperience/en/sites/careers/jobs",
}
LIMIT    = 50
EXPAND   = "requisitionList.workLocation,requisitionList.otherWorkLocations,requisitionList.secondaryLocations"


def _finder(offset: int) -> str:
    return f"findReqs;siteNumber=CX_1001,facetsList=LOCATIONS,limit={LIMIT},offset={offset},sortBy=POSTING_DATES_DESC"


def _fmt_date(s: str) -> str:
    if not s:
        return ""
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").strftime("%b %d, %Y")
    except Exception:
        return ""


async def _fetch(session: AsyncSession, offset: int) -> list[dict]:
    r = await session.get(
        API_URL,
        params={"onlyData": "true", "expand": EXPAND, "finder": _finder(offset)},
        headers=HEADERS,
        timeout=30,
    )
    if r.status_code != 200:
        return []
    return r.json().get("items", [{}])[0].get("requisitionList", [])


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r0 = await session.get(
            API_URL,
            params={"onlyData": "true", "expand": EXPAND, "finder": _finder(0)},
            headers=HEADERS,
            timeout=30,
        )
        r0.raise_for_status()
        data0   = r0.json().get("items", [{}])[0]
        total   = data0.get("TotalJobsCount", 0)
        raw     = data0.get("requisitionList", [])
        print(f"[dell] total={total}")

        sem = asyncio.Semaphore(8)

        async def _guarded(offset):
            async with sem:
                return await _fetch(session, offset)

        pages = await asyncio.gather(*[_guarded(off) for off in range(LIMIT, total + LIMIT, LIMIT)])
        raw += [j for page in pages for j in page]

    seen = set()
    jobs = []
    for j in raw:
        job_id = (j.get("Id") or "").strip()
        title  = (j.get("Title") or "").strip()
        if not job_id or not title or job_id in seen:
            continue
        seen.add(job_id)
        jobs.append({
            "role_id":     f"dell_{job_id}",
            "title":       title,
            "team":        "",
            "location":    (j.get("PrimaryLocation") or "").strip(),
            "posted_date": _fmt_date(j.get("PostedDate") or ""),
            "url":         f"{JOB_BASE}/{job_id}",
            "company":     "Dell",
            "experience":  "",
        })

    print(f"[dell] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")

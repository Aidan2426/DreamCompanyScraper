import asyncio
from curl_cffi.requests import AsyncSession

TENANT   = "hdjq.fa.us2.oraclecloud.com"
SITE     = "CX_1"
API_BASE = f"https://{TENANT}/hcmRestApi/resources/latest/recruitingCEJobRequisitions"
JOB_BASE = f"https://{TENANT}/hcmUI/CandidateExperience/en/sites/{SITE}/job-detail"
HEADERS  = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept":     "application/json",
}
PER_PAGE = 25


async def _fetch(session: AsyncSession, offset: int, sem: asyncio.Semaphore) -> list[dict]:
    async with sem:
        params = (
            f"?expand=requisitionList.secondaryLocations,flexFieldsFacet.values"
            f"&finder=findReqs;siteNumber={SITE}&limit={PER_PAGE}&offset={offset}"
        )
        r = await session.get(API_BASE + params, headers=HEADERS, timeout=30)
        if r.status_code != 200:
            return []
        data = r.json()
        items = data.get("items", [])
        return items[0].get("requisitionList", []) if items else []


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        params0 = (
            f"?expand=requisitionList.secondaryLocations,flexFieldsFacet.values"
            f"&finder=findReqs;siteNumber={SITE}&limit={PER_PAGE}&offset=0"
        )
        r0 = await session.get(API_BASE + params0, headers=HEADERS, timeout=30)
        r0.raise_for_status()
        data0   = r0.json()
        items0  = data0.get("items", [])
        if not items0:
            return []
        total   = items0[0].get("TotalJobsCount", 0)
        page1   = items0[0].get("requisitionList", [])
        print(f"[emerson] total={total}")

        sem     = asyncio.Semaphore(6)
        offsets = range(PER_PAGE, total, PER_PAGE)
        rest    = await asyncio.gather(*[_fetch(session, off, sem) for off in offsets])

    raw = page1 + [j for batch in rest for j in batch]

    seen: set[str] = set()
    jobs: list[dict] = []
    for j in raw:
        job_id = str(j.get("Id") or "").strip()
        title  = (j.get("Title") or "").strip()
        if not job_id or not title or job_id in seen:
            continue
        seen.add(job_id)
        posted = (j.get("PostedDate") or "")
        try:
            from datetime import datetime
            posted = datetime.strptime(posted, "%Y-%m-%d").strftime("%b %d, %Y")
        except Exception:
            posted = ""
        jobs.append({
            "role_id":     f"emerson_{job_id}",
            "title":       title,
            "team":        (j.get("JobFamily") or "").strip(),
            "location":    (j.get("PrimaryLocation") or "").strip(),
            "posted_date": posted,
            "url":         f"{JOB_BASE}/{job_id}",
            "company":     "Emerson",
            "experience":  "",
        })

    print(f"[emerson] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")

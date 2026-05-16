import asyncio
from datetime import datetime
from curl_cffi.requests import AsyncSession

TENANT   = "hdox.fa.us6.oraclecloud.com"
SITE     = "CX_1"
API_BASE = f"https://{TENANT}/hcmRestApi/resources/latest/recruitingCEJobRequisitions"
JOB_BASE = f"https://{TENANT}/hcmUI/CandidateExperience/en/sites/{SITE}/job-detail"
HEADERS  = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept":     "application/json",
}
PER_PAGE = 25


def _fmt_date(s: str) -> str:
    try:
        return datetime.strptime(s, "%Y-%m-%d").strftime("%b %d, %Y")
    except Exception:
        return ""


async def _fetch(session: AsyncSession, offset: int, sem: asyncio.Semaphore) -> list[dict]:
    async with sem:
        params = (
            f"?expand=requisitionList.secondaryLocations,flexFieldsFacet.values"
            f"&finder=findReqs;siteNumber={SITE}&limit={PER_PAGE}&offset={offset}"
        )
        r = await session.get(API_BASE + params, headers=HEADERS, timeout=30)
        if r.status_code != 200:
            return []
        items = r.json().get("items", [])
        return items[0].get("requisitionList", []) if items else []


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        params0 = (
            f"?expand=requisitionList.secondaryLocations,flexFieldsFacet.values"
            f"&finder=findReqs;siteNumber={SITE}&limit={PER_PAGE}&offset=0"
        )
        r0 = await session.get(API_BASE + params0, headers=HEADERS, timeout=30)
        r0.raise_for_status()
        items0 = r0.json().get("items", [])
        if not items0:
            return []
        total  = items0[0].get("TotalJobsCount", 0)
        page1  = items0[0].get("requisitionList", [])
        print(f"[questdiagnostics] total={total}")

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
        jobs.append({
            "role_id":     f"questdiagnostics_{job_id}",
            "title":       title,
            "team":        (j.get("JobFamily") or "").strip(),
            "location":    (j.get("PrimaryLocation") or "").strip(),
            "posted_date": _fmt_date(j.get("PostedDate") or ""),
            "url":         f"{JOB_BASE}/{job_id}",
            "company":     "Quest Diagnostics",
            "experience":  "",
        })

    print(f"[questdiagnostics] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")

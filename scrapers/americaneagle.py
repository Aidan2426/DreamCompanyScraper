import asyncio
from datetime import datetime
from curl_cffi.requests import AsyncSession

API_URL  = "https://hcml.fa.us2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions"
JOB_BASE = "https://hcml.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/AEO-Careers/job"
HEADERS  = {"Accept": "application/json"}
LIMIT       = 25
CONCURRENCY = 6
# Technology and Corporate categories
CATEGORIES  = "300000310850488;300000310850399"


def _fmt_date(iso: str) -> str:
    try:
        return datetime.strptime(iso[:10], "%Y-%m-%d").strftime("%b %d, %Y")
    except Exception:
        return ""


def _finder(offset: int) -> str:
    return f"findReqs;siteNumber=AEO-Careers,selectedCategoriesFacet={CATEGORIES},offset={offset}"


async def _fetch(session: AsyncSession, sem: asyncio.Semaphore, offset: int) -> list[dict]:
    async with sem:
        r = await session.get(
            API_URL,
            params={"finder": _finder(offset), "limit": LIMIT,
                    "expand": "requisitionList.secondaryLocations"},
            headers=HEADERS,
            timeout=30,
        )
        r.raise_for_status()
        return r.json()["items"][0].get("requisitionList", [])


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r0 = await session.get(
            API_URL,
            params={"finder": _finder(0), "limit": LIMIT,
                    "expand": "requisitionList.secondaryLocations"},
            headers=HEADERS,
            timeout=30,
        )
        r0.raise_for_status()
        item0 = r0.json()["items"][0]
        total = item0.get("TotalJobsCount", 0)
        first = item0.get("requisitionList", [])
        print(f"[americaneagle] total={total}")

        sem  = asyncio.Semaphore(CONCURRENCY)
        rest = await asyncio.gather(*[
            _fetch(session, sem, offset)
            for offset in range(LIMIT, total, LIMIT)
        ])

    seen = set()
    jobs = []
    for batch in [first] + list(rest):
        for j in batch:
            job_id = str(j.get("Id", "")).strip()
            title  = (j.get("Title") or "").strip()
            if not job_id or not title or job_id in seen:
                continue
            seen.add(job_id)
            jobs.append({
                "role_id":     f"americaneagle_{job_id}",
                "title":       title,
                "team":        (j.get("JobFamily") or "").strip(),
                "location":    (j.get("PrimaryLocation") or "").strip(),
                "posted_date": _fmt_date(j.get("PostedDate") or ""),
                "url":         f"{JOB_BASE}/{job_id}",
                "company":     "American Eagle",
            })

    print(f"[americaneagle] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])

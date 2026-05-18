import asyncio
from datetime import datetime
from curl_cffi.requests import AsyncSession

API_URL  = "https://api.smartrecruiters.com/v1/companies/CDPROJEKTRED/postings"
JOB_BASE = "https://jobs.smartrecruiters.com/CDPROJEKTRED"
HEADERS  = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept":     "application/json",
}


def _fmt_date(s: str) -> str:
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").strftime("%b %d, %Y")
    except Exception:
        return ""


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r0 = await session.get(API_URL, params={"limit": 100, "offset": 0},
                               headers=HEADERS, timeout=30)
        r0.raise_for_status()
        data  = r0.json()
        total = data.get("totalFound", 0)
        raw   = data.get("content", [])
        print(f"[cdpr] total={total}")

        offset = 100
        while offset < total:
            r = await session.get(API_URL, params={"limit": 100, "offset": offset},
                                  headers=HEADERS, timeout=30)
            if r.status_code != 200:
                break
            raw   += r.json().get("content", [])
            offset += 100

    seen: set[str] = set()
    jobs: list[dict] = []
    for j in raw:
        job_id = (j.get("id") or "").strip()
        title  = (j.get("name") or "").strip()
        if not job_id or not title or job_id in seen:
            continue
        seen.add(job_id)
        loc      = j.get("location") or {}
        loc_parts = [loc.get("city", ""), loc.get("region", ""), loc.get("country", "")]
        location  = ", ".join(p for p in loc_parts if p)
        dept = j.get("department") or {}
        team = (dept.get("label") or "").strip()
        jobs.append({
            "role_id":     f"cdpr_{job_id}",
            "title":       title,
            "team":        team,
            "location":    location,
            "posted_date": _fmt_date(j.get("releasedDate") or ""),
            "url":         f"{JOB_BASE}/{job_id}",
            "company":     "CD Projekt Red",
            "experience":  "",
        })

    print(f"[cdpr] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")

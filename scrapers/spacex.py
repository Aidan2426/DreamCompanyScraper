import asyncio
from datetime import datetime
from curl_cffi.requests import AsyncSession

API_URL  = "https://boards-api.greenhouse.io/v1/boards/spacex/jobs"
JOB_BASE = "https://www.spacex.com/careers/jobs"
HEADERS  = {"User-Agent": "Mozilla/5.0 Chrome/124", "Accept": "application/json"}


def _fmt_date(s: str) -> str:
    if not s:
        return ""
    try:
        return datetime.fromisoformat(s).strftime("%b %d, %Y")
    except Exception:
        return ""


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r = await session.get(API_URL, params={"content": "true"}, headers=HEADERS, timeout=30)
        r.raise_for_status()
        data = r.json()

    raw = data.get("jobs", [])
    print(f"[spacex] total={len(raw)}")

    seen = set()
    jobs = []
    for j in raw:
        job_id = str(j.get("id") or "").strip()
        title  = (j.get("title") or "").strip()
        if not job_id or not title or job_id in seen:
            continue
        seen.add(job_id)
        loc   = j.get("location") or {}
        depts = j.get("departments") or []
        team  = depts[0].get("name", "") if depts else ""
        jobs.append({
            "role_id":     f"spacex_{job_id}",
            "title":       title,
            "team":        team,
            "location":    (loc.get("name") or "").strip(),
            "posted_date": _fmt_date(j.get("first_published") or ""),
            "url":         f"{JOB_BASE}/{job_id}",
            "company":     "SpaceX",
            "experience":  "",
        })

    print(f"[spacex] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["team"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")

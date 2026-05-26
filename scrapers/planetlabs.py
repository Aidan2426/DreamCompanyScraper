import asyncio
from datetime import datetime
from curl_cffi.requests import AsyncSession

API_URL = "https://boards-api.greenhouse.io/v1/boards/planetlabs/jobs"


def _fmt_date(s: str) -> str:
    try:
        return datetime.fromisoformat(s[:19]).strftime("%b %d, %Y")
    except Exception:
        return ""


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r = await session.get(API_URL, params={"content": "true"}, timeout=30)
        r.raise_for_status()
        raw = r.json().get("jobs", [])

    print(f"[planetlabs] total={len(raw)}")

    seen: set[str] = set()
    jobs: list[dict] = []
    for j in raw:
        job_id = str(j.get("id") or "").strip()
        title  = (j.get("title") or "").strip()
        if not job_id or not title or job_id in seen:
            continue
        seen.add(job_id)
        depts   = j.get("departments") or []
        team    = depts[0]["name"] if depts else ""
        offices = j.get("offices") or []
        loc     = (offices[0].get("location") or "") if offices else ""
        if not loc:
            loc = (j.get("location") or {}).get("name", "") or ""
        jobs.append({
            "role_id":     f"planetlabs_{job_id}",
            "title":       title,
            "team":        team,
            "location":    loc,
            "posted_date": _fmt_date(j.get("first_published") or ""),
            "url":         j.get("absolute_url", ""),
            "company":     "Planet Labs",
            "experience":  "",
        })

    print(f"[planetlabs] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")

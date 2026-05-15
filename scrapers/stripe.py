import asyncio
from datetime import datetime
from curl_cffi.requests import AsyncSession

API_URL = "https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true"


def _fmt_date(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%b %d, %Y")
    except Exception:
        return ""


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r = await session.get(API_URL, timeout=30)
        r.raise_for_status()
        jobs_raw = r.json().get("jobs", [])

    print(f"[stripe] total={len(jobs_raw)}")
    seen = set()
    jobs = []
    for j in jobs_raw:
        job_id = str(j.get("id", "")).strip()
        title  = (j.get("title") or "").strip()
        if not job_id or not title or job_id in seen:
            continue
        seen.add(job_id)
        dept = j.get("departments") or []
        jobs.append({
            "role_id":     f"stripe_{job_id}",
            "title":       title,
            "team":        dept[0]["name"] if dept else "",
            "location":    (j.get("location") or {}).get("name", "").strip(),
            "posted_date": _fmt_date(j.get("first_published") or ""),
            "url":         j.get("absolute_url") or "",
            "company":     "Stripe",
        })

    print(f"[stripe] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])

import asyncio
from datetime import datetime
from curl_cffi.requests import AsyncSession

API_URL = "https://api.greenhouse.io/v1/boards/affirm/jobs"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept":     "application/json",
}


def _fmt_date(s: str) -> str:
    if not s:
        return ""
    try:
        return datetime.fromisoformat(s).strftime("%b %d, %Y")
    except Exception:
        return ""


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r = await session.get(API_URL, headers=HEADERS, timeout=30)
        r.raise_for_status()
        raw = r.json().get("jobs", [])
        print(f"[affirm] total={len(raw)}")

    seen: set[str] = set()
    jobs: list[dict] = []
    for j in raw:
        job_id = str(j.get("id") or "").strip()
        title  = (j.get("title") or "").strip()
        if not job_id or not title or job_id in seen:
            continue
        seen.add(job_id)
        depts = j.get("departments") or []
        team  = depts[0].get("name", "") if depts else ""
        jobs.append({
            "role_id":     f"affirm_{job_id}",
            "title":       title,
            "team":        team.strip(),
            "location":    (j.get("location", {}).get("name") or "").strip(),
            "posted_date": _fmt_date(j.get("first_published") or ""),
            "url":         j.get("absolute_url") or "",
            "company":     "Affirm",
            "experience":  "",
        })

    print(f"[affirm] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["team"])
    print(f"Total: {len(jobs)}")

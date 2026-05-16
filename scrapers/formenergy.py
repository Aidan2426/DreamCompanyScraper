import asyncio
from datetime import datetime
from curl_cffi.requests import AsyncSession

API_URL = "https://api.ashbyhq.com/posting-api/job-board/formenergy"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept":     "application/json",
}


def _fmt_date(s: str) -> str:
    if not s:
        return ""
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).strftime("%b %d, %Y")
    except Exception:
        return ""


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r = await session.get(API_URL, headers=HEADERS, timeout=30)
        r.raise_for_status()
        data = r.json()

    raw = data.get("jobs", data) if isinstance(data, dict) else data
    if isinstance(data, dict) and "jobs" not in data:
        raw = []
        for dept in data.get("jobBoard", {}).get("departments", []):
            raw.extend(dept.get("jobPostings", []))
        if not raw:
            raw = data.get("jobPostings", [])

    print(f"[formenergy] total={len(raw)}")

    seen: set[str] = set()
    jobs: list[dict] = []
    for j in raw:
        job_id = (j.get("id") or "").strip()
        title  = (j.get("title") or "").strip()
        if not job_id or not title or job_id in seen:
            continue
        if title.lower().startswith("don't see"):
            continue
        seen.add(job_id)
        jobs.append({
            "role_id":     f"formenergy_{job_id}",
            "title":       title,
            "team":        (j.get("department") or j.get("team") or "").strip(),
            "location":    (j.get("location") or "").strip(),
            "posted_date": _fmt_date(j.get("publishedAt") or ""),
            "url":         j.get("jobUrl") or j.get("applyUrl") or "",
            "company":     "Form Energy",
            "experience":  "",
        })

    print(f"[formenergy] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["team"])
    print(f"Total: {len(jobs)}")

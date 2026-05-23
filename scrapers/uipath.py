import asyncio
from datetime import datetime
from curl_cffi.requests import AsyncSession

API_URL = "https://api.ashbyhq.com/posting-api/job-board/uipath"


def _fmt_date(s: str) -> str:
    try:
        return datetime.fromisoformat(s[:19]).strftime("%b %d, %Y")
    except Exception:
        return ""


def _location(j: dict) -> str:
    loc  = (j.get("location") or "").strip()
    addr = (j.get("address") or {}).get("postalAddress") or {}
    country = (addr.get("addressCountry") or "").strip()
    if country == "United States":
        return f"{loc}, United States" if loc else "United States"
    return loc


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r = await session.get(API_URL, timeout=30)
        r.raise_for_status()
        raw = r.json().get("jobs", [])

    print(f"[uipath] total={len(raw)}")

    seen: set[str] = set()
    jobs: list[dict] = []
    for j in raw:
        job_id = (j.get("id") or "").strip()
        title  = (j.get("title") or "").strip()
        if not job_id or not title or job_id in seen:
            continue
        seen.add(job_id)
        jobs.append({
            "role_id":     f"uipath_{job_id}",
            "title":       title,
            "team":        (j.get("department") or j.get("team") or "").strip(),
            "location":    _location(j),
            "posted_date": _fmt_date(j.get("publishedAt") or ""),
            "url":         j.get("jobUrl", ""),
            "company":     "UiPath",
            "experience":  "",
        })

    print(f"[uipath] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")

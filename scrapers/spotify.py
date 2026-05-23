import asyncio
from datetime import datetime, timezone
from curl_cffi.requests import AsyncSession

API_URL = "https://api.lever.co/v0/postings/spotify?mode=json&limit=500"


def _fmt_ts(ms: int) -> str:
    try:
        return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%b %d, %Y")
    except Exception:
        return ""


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r = await session.get(API_URL, timeout=30)
        r.raise_for_status()
        raw = r.json()

    print(f"[spotify] total={len(raw)}")

    seen: set[str] = set()
    jobs: list[dict] = []
    for j in raw:
        job_id = (j.get("id") or "").strip()
        title  = (j.get("text") or "").strip()
        if not job_id or not title or job_id in seen:
            continue
        seen.add(job_id)
        cats = j.get("categories") or {}
        jobs.append({
            "role_id":     f"spotify_{job_id}",
            "title":       title,
            "team":        cats.get("department") or cats.get("team") or "",
            "location":    cats.get("location") or "",
            "posted_date": _fmt_ts(j.get("createdAt") or 0),
            "url":         j.get("hostedUrl") or f"https://jobs.lever.co/spotify/{job_id}",
            "company":     "Spotify",
            "experience":  "",
        })

    print(f"[spotify] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")

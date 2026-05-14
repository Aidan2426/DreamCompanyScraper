import asyncio
from datetime import datetime
from curl_cffi.requests import AsyncSession

API_URL  = "https://boards-api.greenhouse.io/v1/boards/cloudflare/jobs?content=true"
JOB_BASE = "https://boards.greenhouse.io/cloudflare/jobs"


def _fmt_date(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%b %d, %Y")
    except Exception:
        return ""


def _meta(metadata: list, name: str) -> str:
    for m in metadata or []:
        if m.get("name") == name:
            v = m.get("value")
            if isinstance(v, list):
                return ", ".join(v)
            return v or ""
    return ""


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r = await session.get(API_URL, timeout=30)
        r.raise_for_status()
        raw = r.json().get("jobs", [])
    print(f"[cloudflare] total={len(raw)}")

    seen = set()
    jobs = []
    for j in raw:
        job_id = str(j.get("id", "")).strip()
        title  = (j.get("title") or "").strip()
        if not job_id or not title or job_id in seen:
            continue
        seen.add(job_id)

        meta     = j.get("metadata") or []
        location = _meta(meta, "Job Posting Location") or (j.get("location") or {}).get("name", "")
        team     = _meta(meta, "Career Site Department")

        jobs.append({
            "role_id":     f"cloudflare_{job_id}",
            "title":       title,
            "team":        team,
            "location":    location,
            "posted_date": _fmt_date(j.get("first_published") or ""),
            "url":         j.get("absolute_url") or f"{JOB_BASE}/{job_id}",
            "company":     "Cloudflare",
        })

    print(f"[cloudflare] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])

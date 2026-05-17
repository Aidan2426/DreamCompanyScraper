import asyncio
from datetime import datetime
from curl_cffi.requests import AsyncSession

ALGOLIA_URL = "https://UYBO3E5EHF-dsn.algolia.net/1/indexes/Greenhouse"
HEADERS = {
    "X-Algolia-Application-Id": "UYBO3E5EHF",
    "X-Algolia-API-Key":        "7a9b56bc6afb962030d482030f588e1e",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
}


def _fmt_date(s: str) -> str:
    try:
        return datetime.fromisoformat(s[:19]).strftime("%b %d, %Y")
    except Exception:
        return ""


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r = await session.get(ALGOLIA_URL, params={"query": "", "hitsPerPage": 250},
                              headers=HEADERS, timeout=30)
        r.raise_for_status()
        data = r.json()

    raw = data.get("hits", [])
    print(f"[aurora] total={data.get('nbHits', len(raw))}")

    seen: set[str] = set()
    jobs: list[dict] = []
    for j in raw:
        job_id = str(j.get("id") or "").strip()
        title  = (j.get("title") or "").strip()
        if not job_id or not title or job_id in seen:
            continue
        seen.add(job_id)
        depts = j.get("departments") or []
        team  = depts[0]["name"] if depts else ""
        jobs.append({
            "role_id":     f"aurora_{job_id}",
            "title":       title,
            "team":        team,
            "location":    (j.get("location") or {}).get("name", ""),
            "posted_date": _fmt_date(j.get("first_published") or ""),
            "url":         j.get("absolute_url", ""),
            "company":     "Aurora Innovation",
            "experience":  "",
        })

    print(f"[aurora] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")

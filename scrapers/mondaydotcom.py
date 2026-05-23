import asyncio
from datetime import datetime
from curl_cffi.requests import AsyncSession

API_URL  = "https://www.comeet.co/careers-api/2.0/company/41.00B/positions"
TOKEN    = "14B52C52C67790D3E1296BA37C20"
JOB_BASE = "https://monday.com/careers/"


def _fmt_date(s: str) -> str:
    try:
        return datetime.fromisoformat(s[:19]).strftime("%b %d, %Y")
    except Exception:
        return ""


def _location(loc: dict) -> str:
    if not loc:
        return ""
    city    = (loc.get("city") or "").strip()
    state   = (loc.get("state") or "").strip()
    country = (loc.get("country") or "").strip()
    if country == "US":
        return f"{city}, {state}" if state else f"{city}, United States"
    if city and country:
        return f"{city}, {country}"
    return loc.get("name", "")


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        r = await session.get(API_URL, params={"token": TOKEN}, timeout=30)
        r.raise_for_status()
        raw = r.json()

    print(f"[mondaydotcom] total={len(raw)}")

    seen: set[str] = set()
    jobs: list[dict] = []
    for j in raw:
        uid   = (j.get("uid") or "").strip()
        title = (j.get("name") or "").strip()
        if not uid or not title or uid in seen:
            continue
        seen.add(uid)
        jobs.append({
            "role_id":     f"monday_{uid}",
            "title":       title,
            "team":        (j.get("department") or "").strip(),
            "location":    _location(j.get("location") or {}),
            "posted_date": _fmt_date(j.get("time_updated") or ""),
            "url":         JOB_BASE + uid,
            "company":     "monday.com",
            "experience":  (j.get("experience_level") or "").strip(),
        })

    print(f"[mondaydotcom] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")

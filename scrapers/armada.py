import asyncio
from datetime import datetime
from curl_cffi.requests import AsyncSession

BOARD    = "52d9cac6-58d0-401d-a11a-1d09089cd8ee"
BASE     = f"https://recruiting.ultipro.com/ARM1006ARPA/JobBoard/{BOARD}"
LOAD_URL = BASE + "/JobBoardView/LoadSearchResults"
HEADERS  = {
    "User-Agent":   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept":       "application/json",
    "Content-Type": "application/json",
    "Referer":      BASE + "/",
}
ORDER_BY = [{"Value": "postedDateDesc", "PropertyName": "PostedDate", "Ascending": False}]


def _build_payload(skip: int, top: int = 50) -> dict:
    return {
        "opportunitySearch": {
            "QueryString": "",
            "Filters": [],
            "Top": top,
            "Skip": skip,
            "OrderBy": ORDER_BY,
            "Coordinates": None,
            "Extent": None,
            "ProximitySearchType": 0,
        }
    }


def _fmt_date(s: str) -> str:
    if not s:
        return ""
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).strftime("%b %d, %Y")
    except Exception:
        return ""


def _location(locs: list) -> str:
    if not locs:
        return ""
    addr = locs[0].get("Address") or {}
    city  = addr.get("City") or ""
    state = (addr.get("State") or {}).get("Code") or ""
    return f"{city}, {state}".strip(", ")


async def scrape() -> list[dict]:
    async with AsyncSession(impersonate="chrome124") as session:
        await session.get(BASE + "/?q=&o=postedDateDesc",
                          headers={"User-Agent": HEADERS["User-Agent"]}, timeout=20)

        r0 = await session.post(LOAD_URL, json=_build_payload(0), headers=HEADERS, timeout=30)
        r0.raise_for_status()
        d0    = r0.json()
        total = d0.get("totalCount", 0)
        raw   = d0.get("opportunities", [])
        print(f"[armada] total={total}")

        if total > 50:
            pages = await asyncio.gather(*[
                session.post(LOAD_URL, json=_build_payload(skip), headers=HEADERS, timeout=30)
                for skip in range(50, total, 50)
            ])
            for r in pages:
                if r.status_code == 200 and r.text:
                    raw.extend(r.json().get("opportunities", []))

    seen = set()
    jobs = []
    for j in raw:
        job_id = str(j.get("Id") or "").strip()
        title  = (j.get("Title") or "").strip()
        if not job_id or not title or job_id in seen:
            continue
        seen.add(job_id)
        jobs.append({
            "role_id":     f"armada_{job_id}",
            "title":       title,
            "team":        (j.get("JobCategoryName") or "").strip(),
            "location":    _location(j.get("Locations") or []),
            "posted_date": _fmt_date(j.get("PostedDate") or ""),
            "url":         f"{BASE}/OpportunityDetail?opportunityId={job_id}",
            "company":     "Armada",
            "experience":  "",
        })

    print(f"[armada] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["team"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")

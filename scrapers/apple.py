import asyncio
import math
from curl_cffi.requests import AsyncSession

API_URL  = "https://jobs.apple.com/api/v1/search"
JOB_BASE = "https://jobs.apple.com/en-us/details"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://jobs.apple.com/en-us/search?location=united-states-USA&sort=newest",
    "X-Apple-CSRF-Token": "",
    "locale": "en-us",
}

PAYLOAD_BASE = {
    "query": "",
    "filters": {},
    "locale": "en-us",
    "sort": "newest",
    "format": {"longDate": "MMMM D, YYYY", "mediumDate": "MMM D, YYYY"},
}


async def scrape() -> list[dict]:
    jobs: list[dict] = []
    seen: set[str] = set()

    async with AsyncSession(impersonate="chrome124") as session:
        # Seed session cookies
        await session.get(
            "https://jobs.apple.com/en-us/search?location=united-states-USA&sort=newest",
            timeout=20,
        )

        # Page 1 — get total
        payload = {**PAYLOAD_BASE, "page": 1}
        r = await session.post(API_URL, json=payload, headers=HEADERS, timeout=30)
        r.raise_for_status()
        res = r.json().get("res", {})

        total = res.get("totalRecords", 0)
        total_pages = math.ceil(total / 20)
        print(f"[apple] total={total}, pages={total_pages}")

        _collect(res.get("searchResults") or [], jobs, seen)

        for page in range(2, total_pages + 1):
            payload = {**PAYLOAD_BASE, "page": page}
            r = await session.post(API_URL, json=payload, headers=HEADERS, timeout=30)
            r.raise_for_status()
            results = r.json().get("res", {}).get("searchResults") or []
            if not results:
                break
            _collect(results, jobs, seen)
            if page % 50 == 0:
                print(f"[apple] page {page}/{total_pages}, running={len(jobs)}")

    print(f"[apple] Done. {len(jobs)} jobs.")
    return jobs


def _collect(results: list, jobs: list, seen: set) -> None:
    for j in results:
        # US-only filter
        locs = j.get("locations") or []
        if locs and locs[0].get("countryName") != "United States of America":
            continue

        pos_id = str(j.get("positionId") or j.get("id") or "").strip()
        title  = (j.get("postingTitle") or "").strip()
        if not pos_id or not title or pos_id in seen:
            continue
        seen.add(pos_id)

        team = j.get("team") or {}
        team_name = (team.get("teamName") or team.get("teamCode") or "") if isinstance(team, dict) else str(team)

        raw_loc = locs[0].get("name", "") if locs else ""
        # Append ", United States" so the UI's US-only filter (normalizeLocation) marks isUS=true
        loc_name = f"{raw_loc}, United States" if raw_loc else ""

        jobs.append({
            "role_id":     f"apple_{pos_id}",
            "title":       title,
            "team":        team_name,
            "location":    loc_name,
            "posted_date": j.get("postingDate") or "",
            "url":         f"{JOB_BASE}/{pos_id}",
            "company":     "Apple",
            "experience":  "",
        })


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")

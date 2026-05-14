import httpx
from datetime import datetime

API_URL = "https://api.ashbyhq.com/posting-api/job-board/supercell"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json",
}


def _fmt_date(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%b %d, %Y")
    except Exception:
        return iso[:10] if iso else ""


def scrape() -> list[dict]:
    with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
        r = client.get(API_URL)
        r.raise_for_status()
        raw = r.json().get("jobs", [])

    jobs = []
    for j in raw:
        job_id = j.get("id", "")
        title  = (j.get("title") or "").strip()
        if not title or not job_id:
            continue

        # Combine primary + secondary locations
        locs = [j.get("location", "")]
        for sl in j.get("secondaryLocations", []):
            loc = sl.get("location", "")
            if loc and loc not in locs:
                locs.append(loc)
        location = " | ".join(l for l in locs if l)

        team = j.get("team") or j.get("department") or ""

        jobs.append({
            "role_id":     f"supercell_{job_id}",
            "title":       title,
            "team":        team,
            "location":    location,
            "posted_date": _fmt_date(j.get("publishedAt", "")),
            "url":         j.get("jobUrl", ""),
            "company":     "Supercell",
        })

    print(f"[supercell] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

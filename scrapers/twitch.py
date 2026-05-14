import httpx
from datetime import datetime

API_URL = "https://boards-api.greenhouse.io/v1/boards/twitch/jobs?content=true"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json",
}


def _fmt_date(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%b %d, %Y")
    except Exception:
        return ""


def scrape() -> list[dict]:
    with httpx.Client(timeout=30, headers=HEADERS) as client:
        r = client.get(API_URL)
        r.raise_for_status()
        raw = r.json().get("jobs", [])

    print(f"[twitch] {len(raw)} jobs found")

    seen = set()
    jobs = []
    for j in raw:
        job_id = str(j.get("id") or "").strip()
        title  = (j.get("title") or "").strip()
        if not job_id or not title or job_id in seen:
            continue
        seen.add(job_id)

        depts    = j.get("departments") or []
        team     = depts[0].get("name", "") if depts else ""
        location = (j.get("location") or {}).get("name") or ""

        jobs.append({
            "role_id":     f"twitch_{job_id}",
            "title":       title,
            "team":        team,
            "location":    location,
            "posted_date": _fmt_date(j.get("first_published") or ""),
            "url":         j.get("absolute_url") or f"https://job-boards.greenhouse.io/twitch/jobs/{job_id}",
            "company":     "Twitch",
        })

    print(f"[twitch] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

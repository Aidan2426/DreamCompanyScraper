import httpx
from datetime import datetime

API_URL = "https://boards-api.greenhouse.io/v1/boards/duolingo/jobs"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json",
}


def _fmt_date(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso)
        return dt.strftime("%b %d, %Y")
    except Exception:
        return iso or ""


def scrape() -> list[dict]:
    with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
        r = client.get(API_URL, params={"content": "true"})
        r.raise_for_status()
        jobs_raw = r.json().get("jobs", [])

    jobs = []
    for j in jobs_raw:
        job_id = str(j.get("id", ""))
        title = (j.get("title") or "").strip()
        if not title:
            continue

        dept = j.get("departments", [])
        team = dept[0]["name"] if dept else ""

        location = j.get("location", {}).get("name", "")

        jobs.append({
            "role_id":     f"duolingo_{job_id}",
            "title":       title,
            "team":        team,
            "location":    location,
            "posted_date": _fmt_date(j.get("first_published", "")),
            "url":         j.get("absolute_url", ""),
            "company":     "Duolingo",
        })

    print(f"[duolingo] Done. {len(jobs)} total jobs.")
    return jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

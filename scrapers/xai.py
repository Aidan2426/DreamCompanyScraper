import httpx
from datetime import datetime

API = "https://boards-api.greenhouse.io/v1/boards/xai/jobs"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def _parse_date(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%b %d, %Y")
    except Exception:
        return ""


def scrape() -> list[dict]:
    with httpx.Client(timeout=30, headers=HEADERS) as client:
        r = client.get(API, params={"content": "true"})
        r.raise_for_status()
        jobs_raw = r.json().get("jobs", [])

    jobs = []
    for j in jobs_raw:
        job_id = j.get("id", "")
        title = (j.get("title") or "").strip()
        if not title or not job_id:
            continue

        dept = (j.get("departments") or [{}])[0].get("name", "")
        location = j.get("location", {}).get("name", "")

        jobs.append({
            "role_id":     f"xai_{job_id}",
            "title":       title,
            "team":        dept,
            "location":    location,
            "posted_date": _parse_date(j.get("first_published", "")),
            "url":         j.get("absolute_url", ""),
            "company":     "xAI",
            "experience":  "",
        })

    print(f"[xai] {len(jobs)} jobs")
    return jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

import httpx
from datetime import datetime

API = "https://api.lever.co/v0/postings/palantir"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def _parse_date(ms: int) -> str:
    try:
        return datetime.utcfromtimestamp(ms / 1000).strftime("%b %d, %Y")
    except Exception:
        return ""


def scrape() -> list[dict]:
    with httpx.Client(timeout=30, headers=HEADERS) as client:
        r = client.get(API, params={"mode": "json", "limit": 500})
        r.raise_for_status()
        jobs_raw = r.json()

    jobs = []
    for j in jobs_raw:
        job_id = j.get("id", "")
        title = (j.get("text") or "").strip()
        if not title or not job_id:
            continue

        cats = j.get("categories", {})
        jobs.append({
            "role_id":     f"palantir_{job_id}",
            "title":       title,
            "team":        cats.get("team", ""),
            "location":    cats.get("location", ""),
            "posted_date": _parse_date(j.get("createdAt", 0)),
            "url":         j.get("hostedUrl", ""),
            "company":     "Palantir",
            "experience":  cats.get("commitment", ""),
        })

    print(f"[palantir] {len(jobs)} jobs")
    return jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

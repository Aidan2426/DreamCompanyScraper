import httpx
from datetime import datetime

API_URL = "https://boards-api.greenhouse.io/v1/boards/pinterest/jobs"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Accept": "application/json",
}


def _fmt_date(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%b %d, %Y")
    except Exception:
        return iso[:10] if iso else ""


def _get_team(metadata: list) -> str:
    for m in metadata or []:
        if "careers page department" in (m.get("name") or "").lower():
            val = m.get("value")
            if isinstance(val, list):
                return val[0] if val else ""
            return str(val) if val else ""
    return ""


def scrape() -> list[dict]:
    with httpx.Client(timeout=30, headers=HEADERS) as client:
        r = client.get(API_URL)
        r.raise_for_status()
        jobs_raw = r.json().get("jobs", [])

    print(f"[pinterest] {len(jobs_raw)} jobs found")

    all_jobs = []
    for j in jobs_raw:
        raw_id = str(j.get("id") or "")
        role_id = f"pinterest_{raw_id}" if raw_id else ""
        title = (j.get("title") or "").strip()
        if not role_id or not title:
            continue

        location = (j.get("location") or {}).get("name") or ""
        team = _get_team(j.get("metadata"))
        posted = _fmt_date(j.get("first_published") or "")
        url = j.get("absolute_url") or f"https://www.pinterestcareers.com/jobs/?gh_jid={raw_id}"

        all_jobs.append({
            "role_id":     role_id,
            "title":       title,
            "team":        team,
            "location":    location,
            "posted_date": posted,
            "url":         url,
            "company":     "Pinterest",
        })

    print(f"[pinterest] Done. {len(all_jobs)} jobs.")
    return all_jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

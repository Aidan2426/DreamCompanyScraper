import httpx
from datetime import datetime

API = "https://boards-api.greenhouse.io/v1/boards/roblox/jobs"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def _parse_date(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%b %d, %Y")
    except Exception:
        return ""


def _meta(metadata: list, name: str) -> str:
    for m in metadata or []:
        if m.get("name") == name:
            return m.get("value") or ""
    return ""


def scrape() -> list[dict]:
    with httpx.Client(timeout=30, headers=HEADERS) as client:
        r = client.get(API)
        r.raise_for_status()
        jobs_raw = r.json().get("jobs", [])

    jobs = []
    for j in jobs_raw:
        job_id = j.get("id", "")
        title = (j.get("title") or "").strip()
        if not title or not job_id:
            continue

        meta = j.get("metadata") or []
        group     = _meta(meta, "Group")
        emp_type  = _meta(meta, "Employment Type")

        is_early = group == "Early Career Talent" or emp_type in ("Intern", "Temporary")
        experience = "Early Career" if is_early else ""

        jobs.append({
            "role_id":     f"roblox_{job_id}",
            "title":       title,
            "team":        group,
            "location":    j.get("location", {}).get("name", ""),
            "posted_date": _parse_date(j.get("first_published", "")),
            "url":         j.get("absolute_url", ""),
            "company":     "Roblox",
            "experience":  experience,
        })

    print(f"[roblox] {len(jobs)} jobs")
    return jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

import httpx
from datetime import datetime

API_URL = "https://boards-api.greenhouse.io/v1/boards/figma/jobs"
HEADERS = {"User-Agent": "Mozilla/5.0 Chrome/124", "Accept": "application/json"}


def _fmt_date(s: str) -> str:
    try:
        return datetime.fromisoformat(s).strftime("%b %d, %Y")
    except Exception:
        return ""


def scrape() -> list[dict]:
    with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
        r = client.get(API_URL, params={"content": "true"})
        r.raise_for_status()
        raw = r.json().get("jobs", [])

    print(f"[figma] total={len(raw)}")

    seen = set()
    jobs = []
    for j in raw:
        job_id = str(j.get("id") or "").strip()
        title  = (j.get("title") or "").strip()
        if not job_id or not title or job_id in seen:
            continue
        seen.add(job_id)
        depts = j.get("departments") or []
        team  = depts[0].get("name", "") if depts else ""
        loc   = j.get("location") or {}
        jobs.append({
            "role_id":     f"figma_{job_id}",
            "title":       title,
            "team":        team.strip(),
            "location":    (loc.get("name") or "").strip(),
            "posted_date": _fmt_date(j.get("first_published") or ""),
            "url":         j.get("absolute_url") or "",
            "company":     "Figma",
            "experience":  "",
        })

    print(f"[figma] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")

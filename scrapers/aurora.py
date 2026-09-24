import httpx
from datetime import datetime

# Aurora moved its job board from Greenhouse to Ashby around Sep 2026; the old
# Greenhouse Algolia index (UYBO3E5EHF) stopped updating after that.
API_URL = "https://api.ashbyhq.com/posting-api/job-board/aurora-operations-inc"
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

    print(f"[aurora] total={len(raw)}")
    jobs = []
    for j in raw:
        job_id = j.get("id", "")
        title = (j.get("title") or "").strip()
        if not title or not job_id or j.get("isListed") is False:
            continue
        locs = [j.get("location", "")] + [s.get("location", "") for s in j.get("secondaryLocations") or []]
        jobs.append({
            "role_id":     f"aurora_{job_id}",
            "title":       title,
            "team":        j.get("team") or j.get("department") or "",
            "location":    " | ".join(l for l in locs if l),
            "posted_date": _fmt_date(j.get("publishedAt", "")),
            "url":         j.get("jobUrl", ""),
            "company":     "Aurora Innovation",
        })

    print(f"[aurora] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")

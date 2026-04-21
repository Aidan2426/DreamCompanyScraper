import math
import time
import httpx
from datetime import datetime

API_URL = "https://api.smartrecruiters.com/v1/companies/WesternDigital/postings"
PAGE_SIZE = 100
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json",
}


def _fmt_date(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%b %d, %Y")
    except Exception:
        return iso[:10] if iso else ""


def _parse(data: dict) -> tuple[list[dict], int]:
    total = data.get("totalFound", 0)
    jobs = []
    for j in data.get("content", []):
        job_id = j.get("id", "")
        title = (j.get("name") or "").strip()
        if not title or not job_id:
            continue

        func = j.get("function") or {}
        dept = j.get("department") or {}
        team = func.get("label") or dept.get("label", "")

        loc = j.get("location") or {}
        location = loc.get("fullLocation") or loc.get("city", "")

        url = f"https://careers.smartrecruiters.com/WesternDigital/{job_id}"

        jobs.append({
            "role_id":     f"westerndigital_{job_id}",
            "title":       title,
            "team":        team,
            "location":    location,
            "posted_date": _fmt_date(j.get("releasedDate", "")),
            "url":         url,
            "company":     "Western Digital",
        })
    return jobs, total


def scrape() -> list[dict]:
    all_jobs: list[dict] = []
    seen: set[str] = set()

    with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
        offset = 0
        total = None
        total_pages = None
        page = 1

        while True:
            r = client.get(API_URL, params={"limit": PAGE_SIZE, "offset": offset})
            r.raise_for_status()
            jobs, page_total = _parse(r.json())

            if total is None and page_total > 0:
                total = page_total
                total_pages = math.ceil(total / PAGE_SIZE)
                print(f"[westerndigital] Total: {total}, pages: {total_pages}")

            new = [j for j in jobs if j["role_id"] not in seen]
            for j in new:
                seen.add(j["role_id"])
            all_jobs.extend(new)
            print(f"[westerndigital] Page {page}/{total_pages}: {len(new)} jobs (total {len(all_jobs)})")

            if not jobs or offset + PAGE_SIZE >= total:
                break

            offset += PAGE_SIZE
            page += 1
            time.sleep(0.3)

    print(f"[westerndigital] Done. {len(all_jobs)} total jobs.")
    return all_jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

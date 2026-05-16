import time
import httpx
from datetime import datetime, timezone

API_URL = "https://apply.appcast.io/api/tools/landing_page/qualcomm-careers-us/jobs"
PAGE_SIZE = 10   # API always returns 10 regardless of per_page param
MAX_PAGES = 50   # API returns 500 on page 51+
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://apply.appcast.io/l/qualcomm-careers-us",
}


def _fmt_date(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y")
    except Exception:
        return iso or ""


def _parse(data: dict) -> tuple[list[dict], int, int]:
    total = data.get("jobs_count", 0)
    pages_total = data.get("pages_total", 0)
    jobs = []

    for j in data.get("jobs", []):
        job_id = str(j.get("job_id") or j.get("id", ""))
        title = (j.get("title") or "").strip()
        if not title:
            continue

        loc = j.get("location") or {}
        location = loc.get("location", "") if isinstance(loc, dict) else str(loc)

        jobs.append({
            "role_id":     f"qualcomm_{job_id}",
            "title":       title,
            "team":        "",
            "location":    location,
            "posted_date": _fmt_date(j.get("posted_at", "")),
            "url":         j.get("url", ""),
            "company":     "Qualcomm",
        })

    return jobs, total, pages_total


def scrape() -> list[dict]:
    all_jobs: list[dict] = []
    seen: set[str] = set()

    with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
        page = 1
        total_pages = None

        while True:
            r = client.get(API_URL, params={"page": page, "per_page": PAGE_SIZE})
            r.raise_for_status()
            jobs, total, pages = _parse(r.json())

            if total_pages is None:
                total_pages = pages
                print(f"[qualcomm] Total: {total}, pages: {total_pages}")

            new = [j for j in jobs if j["role_id"] not in seen]
            for j in new:
                seen.add(j["role_id"])
            all_jobs.extend(new)
            print(f"[qualcomm] Page {page}/{total_pages}: {len(new)} jobs (total {len(all_jobs)})")

            if not jobs or page >= min(total_pages, MAX_PAGES):
                break

            page += 1
            time.sleep(0.3)

    print(f"[qualcomm] Done. {len(all_jobs)} total jobs.")
    return all_jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

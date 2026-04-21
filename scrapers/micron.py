import re
import time
import httpx
from datetime import datetime, timezone

PAGE_URL = "https://micron.eightfold.ai/careers"
API_URL = "https://micron.eightfold.ai/api/pcsx/search"
BASE_URL = "https://micron.eightfold.ai"
PAGE_SIZE = 10
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def _fmt_ts(ts) -> str:
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%b %d, %Y")
    except Exception:
        return ""


def _parse(data: dict) -> tuple[list[dict], int]:
    inner = data.get("data", {})
    total = inner.get("count", 0)
    jobs = []

    for p in inner.get("positions", []):
        job_id = str(p.get("id", ""))
        title = (p.get("name") or "").strip()
        if not title:
            continue

        locs = p.get("locations") or []
        location = locs[0] if locs else ""

        path = p.get("positionUrl", "")
        url = f"{BASE_URL}{path}" if path.startswith("/") else path

        jobs.append({
            "role_id":     f"micron_{job_id}",
            "title":       title,
            "team":        p.get("department", ""),
            "location":    location,
            "posted_date": _fmt_ts(p.get("postedTs")),
            "url":         url,
            "company":     "Micron",
        })

    return jobs, total


def scrape() -> list[dict]:
    all_jobs: list[dict] = []
    seen: set[str] = set()

    with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
        # Seed cookies + CSRF token
        r0 = client.get(PAGE_URL, params={"start": 0, "sort_by": "timestamp"},
                        headers={**HEADERS, "Accept": "text/html"})
        r0.raise_for_status()
        csrf = re.search(r'name="_csrf"\s+content="([^"]+)"', r0.text)
        csrf_token = csrf.group(1) if csrf else ""

        api_headers = {
            **HEADERS,
            "Accept": "application/json",
            "X-CSRFToken": csrf_token,
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{PAGE_URL}?start=0&sort_by=timestamp",
        }

        start = 0
        total = None
        page = 1

        while True:
            r = client.get(API_URL,
                           params={"domain": "micron.com", "start": start, "num": PAGE_SIZE, "sort_by": "timestamp"},
                           headers=api_headers)
            r.raise_for_status()
            jobs, page_total = _parse(r.json())

            if total is None and page_total > 0:
                total = page_total
                total_pages = -(-total // PAGE_SIZE)  # ceil div
                print(f"[micron] Total: {total}, pages: {total_pages}")

            new = [j for j in jobs if j["role_id"] not in seen]
            for j in new:
                seen.add(j["role_id"])
            all_jobs.extend(new)
            print(f"[micron] Page {page}/{total_pages}: {len(new)} jobs (total {len(all_jobs)})")

            if not jobs or start + PAGE_SIZE >= total:
                break

            start += PAGE_SIZE
            page += 1
            time.sleep(0.3)

    print(f"[micron] Done. {len(all_jobs)} total jobs.")
    return all_jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

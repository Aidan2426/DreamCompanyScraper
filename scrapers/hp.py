import math
import time
import httpx
from datetime import datetime, timezone

API_URL = "https://apply.hp.com/api/pcsx/search"
PAGE_SIZE = 10
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://apply.hp.com/careers",
}


def _fmt_ts(ts) -> str:
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%b %d, %Y")
    except Exception:
        return ""


def _parse(data: dict) -> tuple[list[dict], int]:
    payload = data.get("data", {})
    total = payload.get("count", 0)
    jobs = []

    for p in payload.get("positions", []):
        job_id = str(p.get("id", ""))
        title = (p.get("name") or "").strip()
        if not title:
            continue

        locs = p.get("locations") or []
        location = locs[0] if locs else ""

        raw_url = p.get("positionUrl") or ""
        if raw_url.startswith("/"):
            raw_url = f"https://apply.hp.com{raw_url}"
        url = raw_url or f"https://apply.hp.com/careers?pid={job_id}&domain=hp.com"

        jobs.append({
            "role_id":     f"hp_{job_id}",
            "title":       title,
            "team":        p.get("department", ""),
            "location":    location,
            "posted_date": _fmt_ts(p.get("postedTs")),
            "url":         url,
            "company":     "HP",
        })

    return jobs, total


def scrape() -> list[dict]:
    all_jobs: list[dict] = []
    seen: set[str] = set()

    with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
        start = 0
        total_pages = None
        page = 1

        while True:
            params = {"domain": "hp.com", "query": "", "location": "", "start": start, "sort_by": "timestamp"}
            r = client.get(API_URL, params=params)
            r.raise_for_status()
            jobs, total = _parse(r.json())

            if total_pages is None:
                total_pages = math.ceil(total / PAGE_SIZE)
                print(f"[hp] Total: {total}, pages: {total_pages}")

            new = [j for j in jobs if j["role_id"] not in seen]
            for j in new:
                seen.add(j["role_id"])
            all_jobs.extend(new)
            print(f"[hp] Page {page}/{total_pages}: {len(new)} jobs (total {len(all_jobs)})")

            if not jobs or start + PAGE_SIZE >= total:
                break

            start += PAGE_SIZE
            page += 1
            time.sleep(0.3)

    print(f"[hp] Done. {len(all_jobs)} total jobs.")
    return all_jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

from datetime import datetime, timezone
import httpx

API_URL = "https://nvidia.eightfold.ai/api/pcsx/search"
BASE_URL = "https://nvidia.eightfold.ai"
PARAMS = {"domain": "nvidia.com", "query": "", "location": "", "sort_by": "postedTs"}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://nvidia.eightfold.ai/careers",
}


def _ts_to_date(ts) -> str:
    if not ts:
        return ""
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%b %d, %Y")
    except Exception:
        return ""


def scrape() -> list[dict]:
    all_jobs: list[dict] = []

    with httpx.Client(timeout=30, headers=HEADERS) as client:
        r = client.get(API_URL, params={**PARAMS, "start": 0})
        r.raise_for_status()
        data = r.json()

        total = data["data"].get("count", 0)
        print(f"[nvidia] {total} total jobs")

        start = 0
        page = 1
        while True:
            if page > 1:
                r = client.get(API_URL, params={**PARAMS, "start": start})
                r.raise_for_status()
                data = r.json()

            positions = data["data"].get("positions", [])
            if not positions:
                break

            for j in positions:
                raw_id  = str(j.get("id", ""))
                role_id = f"nvidia_{raw_id}" if raw_id else ""
                title   = (j.get("name") or "").strip()
                if not role_id or not title:
                    continue

                locs     = j.get("locations") or []
                location = " | ".join(locs)
                team     = (j.get("department") or "").strip()
                posted   = _ts_to_date(j.get("postedTs"))
                path     = j.get("positionUrl") or f"/careers/job/{raw_id}"
                url      = f"{BASE_URL}{path}"

                all_jobs.append({
                    "role_id":     role_id,
                    "title":       title,
                    "team":        team,
                    "location":    location,
                    "posted_date": posted,
                    "url":         url,
                    "company":     "Nvidia",
                })

            print(f"[nvidia] Page {page}: {len(positions)} jobs (total {len(all_jobs)})")
            start += len(positions)
            page  += 1

            if start >= total:
                break

    print(f"[nvidia] Done. {len(all_jobs)} total jobs.")
    return all_jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

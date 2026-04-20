import asyncio
from datetime import datetime, timezone
import httpx

API_URL = "https://explore.jobs.netflix.net/api/apply/v2/jobs"
PARAMS  = {"domain": "netflix.com", "sort_by": "recent", "num": 20}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Accept": "application/json",
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

    with httpx.Client(timeout=30) as client:
        # Get total count first
        r = client.get(API_URL, params={**PARAMS, "start": 0}, headers=HEADERS)
        r.raise_for_status()
        data = r.json()
        total = data.get("count", 0)
        print(f"[netflix] {total} total jobs")

        start = 0
        page  = 1
        while start < total:
            if page > 1:
                r = client.get(API_URL, params={**PARAMS, "start": start}, headers=HEADERS)
                r.raise_for_status()
                data = r.json()

            positions = data.get("positions", [])
            if not positions:
                break

            for j in positions:
                role_id     = str(j.get("id", ""))
                title       = j.get("name", "").strip()
                location    = j.get("location", "").strip()
                team        = j.get("department", "").strip()
                posted_date = _ts_to_date(j.get("t_create"))
                url         = f"https://explore.jobs.netflix.net/careers/job/{role_id}"

                if role_id and title:
                    all_jobs.append({
                        "role_id": role_id, "title": title, "team": team,
                        "location": location, "posted_date": posted_date,
                        "url": url, "company": "Netflix",
                    })

            print(f"[netflix] Page {page}: {len(positions)} jobs (total {len(all_jobs)})")
            start += len(positions)
            page  += 1

    print(f"[netflix] Done. {len(all_jobs)} total jobs.")
    return all_jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

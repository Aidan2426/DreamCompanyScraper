import json
import math
import re
import time
import httpx
from datetime import datetime, timezone

SEARCH_URL = "https://careers.adobe.com/us/en/search-results"
PAGE_SIZE = 10
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,*/*",
    "Accept-Language": "en-US,en;q=0.9",
}


def _extract_jobs(html: str) -> tuple[list[dict], int]:
    total_m = re.search(r'"totalHits"\s*:\s*(\d+)', html)
    total = int(total_m.group(1)) if total_m else 0

    idx = html.find('"jobs":')
    if idx < 0:
        return [], total

    arr_start = html.index('[', idx)
    depth = 0
    for i in range(arr_start, min(arr_start + 2_000_000, len(html))):
        if html[i] == '[':
            depth += 1
        elif html[i] == ']':
            depth -= 1
            if depth == 0:
                raw = json.loads(html[arr_start:i + 1])
                jobs = []
                for j in raw:
                    req_id = j.get("reqId") or j.get("jobId", "")
                    title = (j.get("title") or "").strip()
                    if not title or not req_id:
                        continue

                    cats = j.get("multi_category") or ([j["category"]] if j.get("category") else [])
                    team = " / ".join(cats) if cats else ""

                    locs = j.get("multi_location") or []
                    location = locs[0] if locs else j.get("location", "")

                    posted_raw = j.get("postedDate", "")
                    try:
                        posted = datetime.fromisoformat(
                            posted_raw.replace("+0000", "+00:00")
                        ).strftime("%b %d, %Y")
                    except Exception:
                        posted = posted_raw[:10] if posted_raw else ""

                    apply_url = j.get("applyUrl", "")
                    url = apply_url.removesuffix("/apply") if apply_url.endswith("/apply") else apply_url

                    jobs.append({
                        "role_id":     f"adobe_{req_id}",
                        "title":       title,
                        "team":        team,
                        "location":    location,
                        "posted_date": posted,
                        "url":         url,
                        "company":     "Adobe",
                    })
                return jobs, total

    return [], total


def scrape() -> list[dict]:
    all_jobs: list[dict] = []
    seen: set[str] = set()

    with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
        from_offset = 0
        total = None
        total_pages = None
        page = 1

        while True:
            params = {"from": from_offset}
            if from_offset > 0:
                params["s"] = 1
            r = client.get(SEARCH_URL, params=params)
            r.raise_for_status()

            jobs, page_total = _extract_jobs(r.text)

            if total is None and page_total > 0:
                total = page_total
                total_pages = math.ceil(total / PAGE_SIZE)
                print(f"[adobe] Total: {total}, pages: {total_pages}")

            new = [j for j in jobs if j["role_id"] not in seen]
            for j in new:
                seen.add(j["role_id"])
            all_jobs.extend(new)
            print(f"[adobe] Page {page}/{total_pages}: {len(new)} jobs (total {len(all_jobs)})")

            if not jobs or from_offset + PAGE_SIZE >= total:
                break

            from_offset += PAGE_SIZE
            page += 1
            time.sleep(0.4)

    print(f"[adobe] Done. {len(all_jobs)} total jobs.")
    return all_jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

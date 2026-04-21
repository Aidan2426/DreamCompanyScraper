import math
import time
import httpx
from datetime import datetime, timezone

WIDGETS_URL = "https://careers.cisco.com/widgets"
PAGE_SIZE = 10
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Referer": "https://careers.cisco.com/global/en/search-results",
}
BASE_BODY = {
    "sortBy": "",
    "subsearch": "",
    "jobs": True,
    "counts": True,
    "all_fields": ["category", "raasJobRequisitionType", "country", "state", "city", "type", "RemoteType"],
    "pageName": "search-results",
    "size": PAGE_SIZE,
    "clearAll": False,
    "jdsource": "facets",
    "isSliderEnable": False,
    "pageId": "page4",
    "siteType": "external",
    "keywords": "",
    "global": True,
    "selected_fields": {},
    "lang": "en_global",
    "deviceType": "desktop",
    "country": "global",
    "refNum": "CISCISGLOBAL",
    "ddoKey": "refineSearch",
}


def _fmt_date(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y")
    except Exception:
        return iso or ""


def _parse_response(data: dict) -> tuple[list[dict], int]:
    inner = data.get("refineSearch", {})
    total = inner.get("totalHits", 0)
    raw_jobs = inner.get("data", {}).get("jobs", []) if isinstance(inner.get("data"), dict) else []
    jobs = []

    for j in raw_jobs:
        req_id = j.get("reqId", "")
        title = j.get("title", "").strip()
        if not title:
            continue

        apply_url = j.get("applyUrl", "")
        url = apply_url or f"https://careers.cisco.com/global/en/search-results?reqId={req_id}"

        posted_raw = j.get("postedDate", "") or j.get("dateCreated", "")
        posted_date = _fmt_date(posted_raw)

        jobs.append({
            "role_id":     f"cisco_{req_id}",
            "title":       title,
            "team":        j.get("category", ""),
            "location":    j.get("location", "") or j.get("cityStateCountry", ""),
            "posted_date": posted_date,
            "url":         url,
            "company":     "Cisco",
        })

    return jobs, total


def scrape() -> list[dict]:
    all_jobs: list[dict] = []
    seen: set[str] = set()

    with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
        offset = 0
        total_pages = None
        page = 1

        while True:
            body = {**BASE_BODY, "from": offset}
            r = client.post(WIDGETS_URL, json=body)
            r.raise_for_status()
            jobs, total = _parse_response(r.json())

            if total_pages is None:
                total_pages = math.ceil(total / PAGE_SIZE)
                print(f"[cisco] Total: {total}, pages: {total_pages}")

            new = [j for j in jobs if j["role_id"] not in seen]
            for j in new:
                seen.add(j["role_id"])
            all_jobs.extend(new)
            print(f"[cisco] Page {page}/{total_pages}: {len(new)} jobs (total {len(all_jobs)})")

            if not jobs or offset + PAGE_SIZE >= total:
                break

            offset += PAGE_SIZE
            page += 1
            time.sleep(0.3)

    print(f"[cisco] Done. {len(all_jobs)} total jobs.")
    return all_jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

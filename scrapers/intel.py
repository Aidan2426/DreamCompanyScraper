import math
import re
import time
import httpx
from datetime import date, timedelta

API_URL = "https://intel.wd1.myworkdayjobs.com/wday/cxs/intel/External/jobs"
BASE_URL = "https://intel.wd1.myworkdayjobs.com"
PAGE_SIZE = 20
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Referer": "https://intel.wd1.myworkdayjobs.com/External",
}


def _parse_posted(text: str) -> str:
    """Convert Workday relative date to approximate absolute date string."""
    if not text:
        return ""
    t = text.lower().strip()
    today = date.today()
    if "today" in t:
        return today.strftime("%b %d, %Y")
    m = re.search(r"(\d+)\+?\s+day", t)
    if m:
        days = int(m.group(1))
        return (today - timedelta(days=days)).strftime("%b %d, %Y")
    if "month" in t:
        m2 = re.search(r"(\d+)", t)
        days = int(m2.group(1)) * 30 if m2 else 30
        return (today - timedelta(days=days)).strftime("%b %d, %Y")
    return text


def _job_id(path: str) -> str:
    m = re.search(r"_(JR\w+)$", path)
    return m.group(1) if m else path.rsplit("/", 1)[-1]


def _parse(data: dict) -> tuple[list[dict], int]:
    total = data.get("total", 0)
    jobs = []
    for j in data.get("jobPostings", []):
        path = j.get("externalPath", "")
        job_id = _job_id(path)
        title = (j.get("title") or "").strip()
        if not title:
            continue

        jobs.append({
            "role_id":     f"intel_{job_id}",
            "title":       title,
            "team":        "",
            "location":    j.get("locationsText", ""),
            "posted_date": _parse_posted(j.get("postedOn", "")),
            "url":         f"{BASE_URL}{path}",
            "company":     "Intel",
        })

    return jobs, total


def scrape() -> list[dict]:
    all_jobs: list[dict] = []
    seen: set[str] = set()

    with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
        # Seed cookies
        client.get(f"{BASE_URL}/External")

        offset = 0
        total = 0
        total_pages = None
        page = 1

        while True:
            payload = {"appliedFacets": {}, "limit": PAGE_SIZE, "offset": offset, "searchText": ""}
            r = client.post(API_URL, json=payload)
            r.raise_for_status()
            jobs, page_total = _parse(r.json())

            # Workday only returns total on first page
            if page_total > 0:
                total = page_total
            if total_pages is None and total > 0:
                total_pages = math.ceil(total / PAGE_SIZE)
                print(f"[intel] Total: {total}, pages: {total_pages}")

            new = [j for j in jobs if j["role_id"] not in seen]
            for j in new:
                seen.add(j["role_id"])
            all_jobs.extend(new)
            print(f"[intel] Page {page}/{total_pages}: {len(new)} jobs (total {len(all_jobs)})")

            if not jobs or (total > 0 and offset + PAGE_SIZE >= total):
                break

            offset += PAGE_SIZE
            page += 1
            time.sleep(0.3)

    print(f"[intel] Done. {len(all_jobs)} total jobs.")
    return all_jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

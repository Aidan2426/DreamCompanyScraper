import math
import re
import time
import httpx
from datetime import date, timedelta

API_URL  = "https://sonyglobal.wd1.myworkdayjobs.com/wday/cxs/sonyglobal/SonyGlobalCareers/jobs"
BASE_URL = "https://sonyglobal.wd1.myworkdayjobs.com"
PAGE_SIZE = 20
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Referer": f"{BASE_URL}/SonyGlobalCareers",
}


def _parse_posted(text: str) -> str:
    if not text:
        return ""
    t = text.lower().strip()
    today = date.today()
    if "today" in t:
        return today.strftime("%b %d, %Y")
    if "yesterday" in t:
        return (today - timedelta(days=1)).strftime("%b %d, %Y")
    m = re.search(r"(\d+)\+?\s+day", t)
    if m:
        return (today - timedelta(days=int(m.group(1)))).strftime("%b %d, %Y")
    if "month" in t:
        m2 = re.search(r"(\d+)", t)
        days = int(m2.group(1)) * 30 if m2 else 30
        return (today - timedelta(days=days)).strftime("%b %d, %Y")
    return text


def _job_id(path: str) -> str:
    m = re.search(r"_(JR[\w-]+)$", path)
    return m.group(1) if m else path.rsplit("/", 1)[-1]


def scrape() -> list[dict]:
    all_jobs: list[dict] = []
    seen: set[str] = set()

    with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
        client.get(f"{BASE_URL}/SonyGlobalCareers")

        offset = 0
        total = None
        total_pages = None
        page = 1

        while True:
            payload = {"appliedFacets": {}, "limit": PAGE_SIZE, "offset": offset, "searchText": ""}
            r = client.post(API_URL, json=payload)
            r.raise_for_status()
            data = r.json()

            if total is None:
                total = data.get("total", 0)
                total_pages = math.ceil(total / PAGE_SIZE) if total else 1
                print(f"[sony] Total: {total}, pages: {total_pages}")

            new = []
            for j in data.get("jobPostings", []):
                path = j.get("externalPath", "")
                job_id = _job_id(path)
                title = (j.get("title") or "").strip()
                if not title or job_id in seen:
                    continue
                seen.add(job_id)
                new.append({
                    "role_id":     f"sony_{job_id}",
                    "title":       title,
                    "team":        "",
                    "location":    j.get("locationsText", ""),
                    "posted_date": _parse_posted(j.get("postedOn", "")),
                    "url":         f"{BASE_URL}{path}",
                    "company":     "Sony",
                    "experience":  "",
                })

            all_jobs.extend(new)
            print(f"[sony] Page {page}/{total_pages}: {len(new)} jobs (total {len(all_jobs)})")

            if not data.get("jobPostings") or offset + PAGE_SIZE >= total:
                break

            offset += PAGE_SIZE
            page += 1
            time.sleep(0.3)

    print(f"[sony] Done. {len(all_jobs)} total jobs.")
    return all_jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

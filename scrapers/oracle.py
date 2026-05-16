import math
import time
import httpx
from datetime import datetime

API_URL = "https://eeho.fa.us2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions"
PAGE_SIZE = 100
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://careers.oracle.com/",
}
EXPAND = (
    "requisitionList.workLocation,"
    "requisitionList.otherWorkLocations,"
    "requisitionList.secondaryLocations,"
    "flexFieldsFacet.values,"
    "requisitionList.requisitionFlexFields"
)
FACETS = "LOCATIONS%3BWORK_LOCATIONS%3BWORKPLACE_TYPES%3BTITLES%3BCATEGORIES%3BORGANIZATIONS%3BPOSTING_DATES%3BFLEX_FIELDS"


def _finder(offset: int) -> str:
    return f"findReqs;siteNumber=CX_45001,facetsList={FACETS},limit={PAGE_SIZE},sortBy=POSTING_DATES_DESC,offset={offset}"


def _fmt_date(raw: str) -> str:
    try:
        return datetime.strptime(raw, "%Y-%m-%d").strftime("%b %d, %Y")
    except Exception:
        return raw or ""


def _parse(data: dict) -> tuple[list[dict], int]:
    items = data.get("items", [])
    if not items:
        return [], 0

    item = items[0]
    total = item.get("TotalJobsCount", 0)
    jobs = []

    for j in item.get("requisitionList", []):
        job_id = str(j.get("Id", ""))
        title = (j.get("Title") or "").strip()
        if not title:
            continue

        location = j.get("PrimaryLocation", "")

        jobs.append({
            "role_id":     f"oracle_{job_id}",
            "title":       title,
            "team":        j.get("JobFamily", "") or j.get("JobFunction", ""),
            "location":    location,
            "posted_date": _fmt_date(j.get("PostedDate", "")),
            "url":         f"https://careers.oracle.com/en/sites/jobsearch/job/{job_id}",
            "company":     "Oracle",
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
            params = {"onlyData": "true", "expand": EXPAND, "finder": _finder(offset)}
            r = client.get(API_URL, params=params)
            r.raise_for_status()
            jobs, total = _parse(r.json())

            if total_pages is None:
                total_pages = math.ceil(total / PAGE_SIZE)
                print(f"[oracle] Total: {total}, pages: {total_pages}")

            new = [j for j in jobs if j["role_id"] not in seen]
            for j in new:
                seen.add(j["role_id"])
            all_jobs.extend(new)
            print(f"[oracle] Page {page}/{total_pages}: {len(new)} jobs (total {len(all_jobs)})")

            if not jobs or offset + PAGE_SIZE >= total:
                break

            offset += PAGE_SIZE
            page += 1
            time.sleep(0.3)

    print(f"[oracle] Done. {len(all_jobs)} total jobs.")
    return all_jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

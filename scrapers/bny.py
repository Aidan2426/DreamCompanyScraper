import math
import time
import httpx
from datetime import datetime

BASE     = "https://eofe.fa.us2.oraclecloud.com"
API_URL  = BASE + "/hcmRestApi/resources/latest/recruitingCEJobRequisitions"
JOB_BASE = BASE + "/hcmUI/CandidateExperience/en/sites/BNY-Careers/job"
PAGE_SIZE = 100
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": BASE + "/",
}
EXPAND  = "requisitionList.workLocation,requisitionList.requisitionFlexFields"
FACETS  = "LOCATIONS%3BWORK_LOCATIONS%3BWORKPLACE_TYPES%3BTITLES%3BCATEGORIES%3BORGANIZATIONS%3BPOSTING_DATES%3BFLEX_FIELDS"


def _finder(offset: int) -> str:
    return f"findReqs;siteNumber=BNY-Careers,facetsList={FACETS},limit={PAGE_SIZE},sortBy=POSTING_DATES_DESC,offset={offset}"


def _fmt_date(raw: str) -> str:
    try:
        return datetime.strptime(raw, "%Y-%m-%d").strftime("%b %d, %Y")
    except Exception:
        return raw or ""


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
            data = r.json()

            items = data.get("items", [])
            if not items:
                break
            item = items[0]

            if total_pages is None:
                total = item.get("TotalJobsCount", 0)
                total_pages = math.ceil(total / PAGE_SIZE)
                print(f"[bny] Total: {total}, pages: {total_pages}")

            new = []
            for j in item.get("requisitionList", []):
                job_id = str(j.get("Id", ""))
                title  = (j.get("Title") or "").strip()
                if not job_id or not title or job_id in seen:
                    continue
                seen.add(job_id)
                new.append({
                    "role_id":     f"bny_{job_id}",
                    "title":       title,
                    "team":        (j.get("JobFamily") or j.get("JobFunction") or "").strip(),
                    "location":    (j.get("PrimaryLocation") or "").strip(),
                    "posted_date": _fmt_date(j.get("PostedDate") or ""),
                    "url":         f"{JOB_BASE}/{job_id}",
                    "company":     "BNY",
                    "experience":  (j.get("ManagerLevel") or "").strip(),
                })

            all_jobs.extend(new)
            print(f"[bny] Page {page}/{total_pages}: {len(new)} jobs (total {len(all_jobs)})")

            if offset + PAGE_SIZE >= item.get("TotalJobsCount", 0):
                break
            offset += PAGE_SIZE
            page += 1
            time.sleep(0.3)

    print(f"[bny] Done. {len(all_jobs)} jobs.")
    return all_jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")

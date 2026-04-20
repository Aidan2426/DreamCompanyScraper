import re
import time
import httpx

API_URL = "https://www.amazon.jobs/en-gb/search.json"
CATEGORIES = [
    "software-development",
    "machine-learning-science",
    "data-science",
    "database-administration",
    "hardware-development",
    "solutions-architect",
    "systems-quality-security-engineering",
    "administrative-support",
    "project-program-product-management-technical",
    "operations-it-support-engineering",
]
PAGE_SIZE = 10
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Accept": "application/json",
}


def _build_params(offset: int) -> dict:
    params = [
        ("offset", offset),
        ("result_limit", PAGE_SIZE),
        ("sort", "recent"),
    ]
    for cat in CATEGORIES:
        params.append(("category[]", cat))
    return params


def scrape() -> list[dict]:
    all_jobs: list[dict] = []
    seen: set[str] = set()

    with httpx.Client(timeout=30, headers=HEADERS) as client:
        # Get total
        r = client.get(API_URL, params=_build_params(0))
        r.raise_for_status()
        data = r.json()
        total = data.get("hits", 0)
        total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
        print(f"[amazon] {total} jobs across {total_pages} pages")

        offset = 0
        page = 1
        while offset < total:
            if page > 1:
                time.sleep(0.3)  # be polite
                r = client.get(API_URL, params=_build_params(offset))
                r.raise_for_status()
                data = r.json()

            jobs = data.get("jobs", [])
            if not jobs:
                break

            for j in jobs:
                role_id = str(j.get("id") or j.get("job_id") or "")
                if not role_id or role_id in seen:
                    continue
                seen.add(role_id)

                title    = (j.get("title") or "").strip()
                location = (j.get("location") or j.get("normalized_location") or "").strip()
                team     = (j.get("job_category") or j.get("business_category") or "").strip()
                posted   = (j.get("posted_date") or "").strip()
                # url_next_step is apply page — extract numeric ID for listing URL
                apply_url = j.get("url_next_step") or ""
                num_match = re.search(r"/jobs/(\d+)", apply_url)
                numeric_id = num_match.group(1) if num_match else ""
                slug = (j.get("title") or "").lower().strip()
                slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
                job_url = f"https://www.amazon.jobs/en-gb/jobs/{numeric_id}/{slug}" if numeric_id else apply_url

                if role_id and title:
                    all_jobs.append({
                        "role_id":    role_id,
                        "title":      title,
                        "team":       team,
                        "location":   location,
                        "posted_date": posted,
                        "url":        job_url,
                        "company":    "Amazon",
                    })

            print(f"[amazon] Page {page}/{total_pages}: {len(jobs)} jobs (total {len(all_jobs)})")
            offset += PAGE_SIZE
            page += 1

    print(f"[amazon] Done. {len(all_jobs)} total jobs.")
    return all_jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

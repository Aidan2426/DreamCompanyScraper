import httpx

API_URL = "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Accept": "application/json",
}


def scrape() -> list[dict]:
    with httpx.Client(timeout=30, headers=HEADERS) as client:
        r = client.get(API_URL)
        r.raise_for_status()
        data = r.json()

    jobs_raw = data.get("jobs", [])
    print(f"[anthropic] {len(jobs_raw)} jobs found")

    all_jobs = []
    for j in jobs_raw:
        raw_id = str(j.get("id") or "")
        role_id = f"anthropic_{raw_id}" if raw_id else ""
        title = (j.get("title") or "").strip()
        if not role_id or not title:
            continue

        departments = j.get("departments") or []
        team = departments[0]["name"] if departments else ""

        location = (j.get("location") or {}).get("name") or ""
        location = location.strip()

        posted = (j.get("first_published") or "")[:10]  # YYYY-MM-DD
        url = j.get("absolute_url") or f"https://job-boards.greenhouse.io/anthropic/jobs/{raw_id}"

        all_jobs.append({
            "role_id":     role_id,
            "title":       title,
            "team":        team,
            "location":    location,
            "posted_date": posted,
            "url":         url,
            "company":     "Anthropic",
        })

    print(f"[anthropic] Done. {len(all_jobs)} jobs.")
    return all_jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

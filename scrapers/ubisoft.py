import httpx
from datetime import datetime

ALGOLIA_APP_ID = "AVCVYSEJS1"
ALGOLIA_API_KEY = "d2ec5782c4eb549092cfa4ed5062599a"
ALGOLIA_INDEX   = "jobs_en-us_default"
API_URL = f"https://{ALGOLIA_APP_ID}-dsn.algolia.net/1/indexes/*/queries"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "X-Algolia-Application-Id": ALGOLIA_APP_ID,
    "X-Algolia-API-Key": ALGOLIA_API_KEY,
    "Content-Type": "application/json",
}


def scrape() -> list[dict]:
    payload = {"requests": [{"indexName": ALGOLIA_INDEX, "params": "hitsPerPage=500&page=0"}]}
    with httpx.Client(timeout=30, headers=HEADERS) as client:
        r = client.post(API_URL, json=payload)
        r.raise_for_status()
        hits = r.json()["results"][0]["hits"]

    jobs = []
    for h in hits:
        job_id = h.get("objectID", "")
        title  = (h.get("title") or "").strip()
        if not title or not job_id:
            continue

        city    = h.get("city", "")
        country = h.get("countryCode", "").upper()
        location = f"{city}, {country}" if city and country else city or country

        ts = h.get("createdAtUnix", 0)
        try:
            posted = datetime.utcfromtimestamp(ts).strftime("%b %d, %Y") if ts else ""
        except Exception:
            posted = ""

        jobs.append({
            "role_id":     f"ubisoft_{job_id}",
            "title":       title,
            "team":        h.get("department", ""),
            "location":    location,
            "posted_date": posted,
            "url":         h.get("link", ""),
            "company":     "Ubisoft",
            "experience":  h.get("experienceLevel", ""),
        })

    print(f"[ubisoft] {len(jobs)} jobs")
    return jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

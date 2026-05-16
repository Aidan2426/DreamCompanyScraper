import httpx
import re
import json
from datetime import datetime, timezone

API_URL = "https://jobsapi-internal.m-cloud.io/api/job"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, */*",
    "Referer": "https://jobs.universalparks.com/",
}


def _fmt_date(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y")
    except Exception:
        return iso or ""


def _location(j: dict) -> str:
    parts = [j.get("primary_city", ""), j.get("primary_state", ""), j.get("primary_country", "")]
    return ", ".join(p for p in parts if p)


def _parse(data: dict) -> list[dict]:
    jobs = []
    for j in data.get("queryResult", []):
        job_id = str(j.get("id", ""))
        title = (j.get("title") or "").strip()
        if not title:
            continue

        url = j.get("url") or j.get("seo_url") or f"https://jobs.universalparks.com/job/{job_id}/"

        jobs.append({
            "role_id":     f"universal_{job_id}",
            "title":       title,
            "team":        j.get("primary_category", "") or j.get("function", ""),
            "location":    _location(j),
            "posted_date": _fmt_date(j.get("open_date", "")),
            "url":         url,
            "company":     "Universal Parks & Resorts",
        })
    return jobs


def scrape() -> list[dict]:
    with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
        params = {
            "sortfield": "open_date",
            "sortorder": "descending",
            "Limit": 500,
            "Organization": 1717,
            "offset": 1,
        }
        r = client.get(API_URL, params=params)
        r.raise_for_status()

        text = r.text
        m = re.match(r"^[^(]+\((.+)\)$", text.strip(), re.DOTALL)
        data = json.loads(m.group(1)) if m else r.json()

        total = data.get("totalHits", 0)
        jobs = _parse(data)
        print(f"[universal] Total: {total}, scraped: {len(jobs)}")
        return jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

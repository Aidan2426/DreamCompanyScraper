import time
import httpx
from datetime import datetime, timezone

API_URL = "https://www-api.ibm.com/search/api/v2"
PAGE_SIZE = 30
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Referer": "https://www.ibm.com/",
}

BASE_PAYLOAD = {
    "appId": "careers",
    "scopes": ["careers2"],
    "query": {"bool": {"must": []}},
    "aggs": {
        "field_keyword_172": {"filter": {"match_all": {}}, "aggs": {"field_keyword_17": {"terms": {"field": "field_keyword_17", "size": 6}}, "field_keyword_17_count": {"cardinality": {"field": "field_keyword_17"}}}},
        "field_keyword_083": {"filter": {"match_all": {}}, "aggs": {"field_keyword_08": {"terms": {"field": "field_keyword_08", "size": 6}}, "field_keyword_08_count": {"cardinality": {"field": "field_keyword_08"}}}},
        "field_keyword_184": {"filter": {"match_all": {}}, "aggs": {"field_keyword_18": {"terms": {"field": "field_keyword_18", "size": 6}}, "field_keyword_18_count": {"cardinality": {"field": "field_keyword_18"}}}},
        "field_keyword_055": {"filter": {"match_all": {}}, "aggs": {"field_keyword_05": {"terms": {"field": "field_keyword_05", "size": 1000}}, "field_keyword_05_count": {"cardinality": {"field": "field_keyword_05"}}}},
    },
    "sort": [{"dcdate": "desc"}, {"_score": "desc"}],
    "lang": "zz",
    "localeSelector": {},
    "sm": {"query": "", "lang": "zz"},
    "_source": ["_id", "title", "url", "field_keyword_08", "field_keyword_18", "field_keyword_19"],
}


def _epoch_ms_to_date(ms) -> str:
    try:
        return datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc).strftime("%b %d, %Y")
    except Exception:
        return ""


def _parse_response(data: dict) -> tuple[list[dict], int]:
    hits = data.get("hits", {})
    total = hits.get("total", {}).get("value", 0)
    jobs = []

    for hit in hits.get("hits", []):
        src = hit.get("_source", {})
        url = src.get("url", "")

        job_id = ""
        if "jobId=" in url:
            job_id = url.split("jobId=")[-1].split("&")[0]
        if not job_id:
            job_id = hit.get("_id", "")[:16]

        sort_vals = hit.get("sort", [])
        posted_date = _epoch_ms_to_date(sort_vals[0]) if sort_vals else ""

        jobs.append({
            "role_id":     f"ibm_{job_id}",
            "title":       src.get("title", "").strip(),
            "team":        src.get("field_keyword_08", ""),
            "location":    src.get("field_keyword_19", ""),
            "posted_date": posted_date,
            "url":         url,
            "company":     "IBM",
        })

    return jobs, total


def scrape() -> list[dict]:
    all_jobs: list[dict] = []
    seen: set[str] = set()

    with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
        offset = 0
        total_pages = None
        page = 1
        fail_streak = 0

        while True:
            payload = {**BASE_PAYLOAD, "size": PAGE_SIZE, "from": offset}
            try:
                r = client.post(API_URL, json=payload)
                r.raise_for_status()
                data = r.json()
            except Exception as e:
                fail_streak += 1
                print(f"[ibm] Page {page} failed: {e}")
                if fail_streak >= 3:
                    print(f"[ibm] {fail_streak} consecutive failed pages, stopping")
                    break
                time.sleep(1)
                continue
            fail_streak = 0

            jobs, total = _parse_response(data)

            if total_pages is None:
                total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
                print(f"[ibm] Total jobs: {total}, pages: {total_pages}")

            new = [j for j in jobs if j["role_id"] not in seen]
            for j in new:
                seen.add(j["role_id"])
            all_jobs.extend(new)
            print(f"[ibm] Page {page}/{total_pages}: {len(new)} jobs (total {len(all_jobs)})")

            if not jobs or offset + PAGE_SIZE >= total:
                break

            offset += PAGE_SIZE
            page += 1
            time.sleep(0.3)

    print(f"[ibm] Done. {len(all_jobs)} total jobs.")
    return all_jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

from curl_cffi.requests import Session
from datetime import datetime

SEARCH_URL = "https://www.yahooinc.com/careers/calls/makeVespaCalls.php"
SEED_URL   = "https://www.yahooinc.com/careers/search.html"
HEADERS    = {
    "Origin":       "https://www.yahooinc.com",
    "Referer":      SEARCH_URL,
    "Content-Type": "application/x-www-form-urlencoded",
}


def _fmt_date(iso: str) -> str:
    try:
        return datetime.strptime(iso, "%Y-%m-%d").strftime("%b %d, %Y")
    except Exception:
        return ""


def _post(session: Session, offset: int) -> dict:
    r = session.post(
        SEARCH_URL,
        data={
            "searchContent": "",
            "action":        "searchJobs",
            "job_cats":      "",
            "job_brands":    "",
            "job_locations": "",
            "job_levels":    "",
            "offset":        offset,
            "check":         "false",
        },
        headers=HEADERS,
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def scrape() -> list[dict]:
    with Session(impersonate="chrome124") as s:
        s.get(SEED_URL, timeout=15)

        first   = _post(s, 0)
        total   = first.get("TotalResultCount", 0)
        print(f"[yahoo] TotalResultCount={total}")

        if total <= 20:
            raw = first.get("data", [])
        else:
            last = _post(s, total - 20)
            raw  = last.get("data", [])

    seen = set()
    jobs = []
    for item in raw:
        if item.get("id") == "ExampleHit":
            continue
        f = item.get("fields", {})
        req_id = (f.get("ReqNo") or "").strip()
        title  = (f.get("JobTitle") or "").strip()
        if not req_id or not title or req_id in seen:
            continue
        seen.add(req_id)
        jobs.append({
            "role_id":     f"yahoo_{req_id}",
            "title":       title,
            "team":        (f.get("JobCategory") or "").strip(),
            "location":    (f.get("PrimaryLocation") or "").strip(),
            "posted_date": _fmt_date(f.get("PostingDate") or ""),
            "url":         (f.get("ApplyLink") or "").strip(),
            "company":     "Yahoo",
            "experience":  (f.get("JobLevel") or "").strip(),
        })

    print(f"[yahoo] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])

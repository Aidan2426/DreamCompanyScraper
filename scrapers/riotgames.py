from curl_cffi.requests import Session
from html import unescape
import re
import json

PAGE_URL = "https://www.riotgames.com/en/work-with-us"
BASE_URL = "https://www.riotgames.com"


def _extract_jobs(html: str) -> list[dict]:
    idx = html.find("&quot;jobs&quot;:[{&quot;title")
    if idx < 0:
        return []
    chunk = html[html.rfind("data-props", 0, idx):]
    start = chunk.index('"') + 1
    rest  = chunk[start:]
    raw   = rest[:rest.index('"')]
    obj   = json.loads(unescape(raw))
    return obj.get("jobs", [])


def scrape() -> list[dict]:
    with Session(impersonate="chrome124") as s:
        r = s.get(PAGE_URL, timeout=30)
        r.raise_for_status()

    raw = _extract_jobs(r.text)
    print(f"[riotgames] {len(raw)} jobs in page")

    seen = set()
    jobs = []
    for j in raw:
        internal_id = (j.get("internalId") or "").strip()
        title       = (j.get("title")      or "").strip()
        j_url       = (j.get("url")        or "").strip()
        if not internal_id or not title or internal_id in seen:
            continue
        seen.add(internal_id)
        jobs.append({
            "role_id":     f"riot_{internal_id}",
            "title":       title,
            "team":        (j.get("craft")  or "").strip(),
            "location":    (j.get("office") or "").strip(),
            "posted_date": "",
            "url":         BASE_URL + j_url if j_url else "",
            "company":     "Riot Games",
        })

    print(f"[riotgames] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["url"])

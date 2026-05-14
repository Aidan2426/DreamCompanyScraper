import httpx
from xml.etree import ElementTree as ET
from email.utils import parsedate_to_datetime
from curl_cffi.requests import Session

FEED_URL = "https://www.dropbox.jobs/en/jobs/xml/?rss=true"


def _fmt_date(rfc: str) -> str:
    try:
        return parsedate_to_datetime(rfc).strftime("%b %d, %Y")
    except Exception:
        return ""


def _location(job: ET.Element) -> str:
    city    = (job.findtext("city")    or "").strip()
    state   = (job.findtext("state")   or "").strip()
    country = (job.findtext("country") or "").strip()
    if city and state:
        return f"{city}, {state}"
    if city and country:
        return f"{city}, {country}"
    return city or state or country


def scrape() -> list[dict]:
    with Session(impersonate="chrome124") as s:
        r = s.get(FEED_URL, timeout=30)
        r.raise_for_status()

    root     = ET.fromstring(r.content)
    jobs_xml = root.findall("job")
    print(f"[dropbox] {len(jobs_xml)} jobs in feed")

    seen = set()
    jobs = []
    for j in jobs_xml:
        api_id = (j.findtext("apijobid")  or "").strip()
        title  = (j.findtext("title")    or "").strip()
        if not api_id or not title or api_id in seen:
            continue
        seen.add(api_id)
        jobs.append({
            "role_id":     f"dropbox_{api_id}",
            "title":       title,
            "team":        (j.findtext("category") or "").strip(),
            "location":    _location(j),
            "posted_date": _fmt_date(j.findtext("date") or ""),
            "url":         (j.findtext("url") or "").strip(),
            "company":     "Dropbox",
        })

    print(f"[dropbox] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

import httpx
from xml.etree import ElementTree as ET
from email.utils import parsedate_to_datetime

FEED_URL = "https://careers.salesforce.com/en/jobs/xml/?rss=true"
HEADERS  = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/xml, text/xml, */*",
}


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
    with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
        r = client.get(FEED_URL)
        r.raise_for_status()

    root = ET.fromstring(r.content)
    jobs_xml = root.findall("job")
    print(f"[salesforce] {len(jobs_xml)} jobs in feed")

    seen = set()
    jobs = []
    for j in jobs_xml:
        req_id = (j.findtext("requisitionid") or "").strip()
        title  = (j.findtext("title")         or "").strip()
        if not req_id or not title or req_id in seen:
            continue
        seen.add(req_id)
        jobs.append({
            "role_id":     f"salesforce_{req_id}",
            "title":       title,
            "team":        (j.findtext("category") or "").strip(),
            "location":    _location(j),
            "posted_date": _fmt_date(j.findtext("date") or ""),
            "url":         (j.findtext("url") or "").strip(),
            "company":     "Salesforce",
        })

    print(f"[salesforce] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print({k: v.encode("ascii", "replace").decode() for k, v in j.items()})

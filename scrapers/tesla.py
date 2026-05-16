import json
import re
import time
from datetime import datetime

import undetected_chromedriver as uc

JOB_BASE = "https://www.tesla.com/careers/search/job"
STATE_API = "/cua-api/apps/careers/state"


def _fmt_date(s: str) -> str:
    if not s:
        return ""
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).strftime("%b %d, %Y")
    except Exception:
        return ""


def _slug(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s.strip())
    return s


def scrape() -> list[dict]:
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(options=options, headless=False)
    try:
        driver.get("https://www.tesla.com/careers/search/?site=US")
        time.sleep(18)

        raw_json = driver.execute_script(
            "return fetch('/cua-api/apps/careers/state',{credentials:'include',"
            "headers:{'Accept':'application/json'}}).then(r=>r.json()).then(d=>JSON.stringify(d));"
        )
        time.sleep(4)
        data = json.loads(raw_json)
    finally:
        try:
            driver.quit()
        except Exception:
            pass

    lookup    = data.get("lookup", {})
    depts     = lookup.get("departments", {})
    locations = lookup.get("locations", {})
    listings  = data.get("listings", [])
    print(f"[tesla] total={len(listings)}")

    seen = set()
    jobs = []
    for j in listings:
        job_id = str(j.get("id") or "").strip()
        title  = (j.get("t") or "").strip()
        if not job_id or not title or job_id in seen:
            continue
        seen.add(job_id)
        dept = depts.get(str(j.get("dp", "")), "")
        loc  = locations.get(str(j.get("l", "")), "")
        slug = _slug(title)
        jobs.append({
            "role_id":     f"tesla_{job_id}",
            "title":       title,
            "team":        dept,
            "location":    loc,
            "posted_date": _fmt_date(j.get("pu") or ""),
            "url":         f"{JOB_BASE}/{slug}-{job_id}",
            "company":     "Tesla",
            "experience":  "",
        })

    print(f"[tesla] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["team"])
    print(f"Total: {len(jobs)}")

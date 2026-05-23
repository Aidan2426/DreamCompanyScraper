import asyncio
import re
import urllib.request
from datetime import datetime
from curl_cffi.requests import AsyncSession

SITEMAP_URL = "https://careers.dolby.com/sitemap.xml"
JOB_BASE    = "https://careers.dolby.com"


def _parse_date(s: str) -> str:
    try:
        return datetime.strptime(s.strip(), "%a %b %d %H:%M:%S UTC %Y").strftime("%b %d, %Y")
    except Exception:
        return ""


def _location(city: str, state: str, country: str) -> str:
    if country == "US" and city:
        return f"{city}, {state}" if state else f"{city}, United States"
    if city and country:
        return f"{city}, {country}"
    return city


async def _fetch_job(session: AsyncSession, url: str, sem: asyncio.Semaphore) -> dict | None:
    async with sem:
        try:
            r = await session.get(url, timeout=20)
        except Exception:
            return None
    html = r.text
    m = re.search(r"<title>(.*?) Job Details", html)
    if not m:
        return None
    title = m.group(1).strip()

    job_id = url.rstrip("/").rsplit("/", 1)[-1]

    city    = re.search(r'addressLocality" content="([^"]+)"', html)
    state   = re.search(r'addressRegion" content="([^"]+)"', html)
    country = re.search(r'addressCountry" content="([^"]+)"', html)
    date    = re.search(r'datePosted" content="([^"]+)"', html)

    return {
        "role_id":     f"dolby_{job_id}",
        "title":       title,
        "team":        "",
        "location":    _location(
                           city.group(1) if city else "",
                           state.group(1) if state else "",
                           country.group(1) if country else "",
                       ),
        "posted_date": _parse_date(date.group(1) if date else ""),
        "url":         url,
        "company":     "Dolby",
        "experience":  "",
    }


async def scrape() -> list[dict]:
    req = urllib.request.Request(SITEMAP_URL, headers={"User-Agent": "Mozilla/5.0"})
    sitemap_html = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", errors="ignore")
    job_urls = re.findall(
        r"<loc>(https://careers\.dolby\.com/job/[^<]+)</loc>",
        sitemap_html,
    )
    print(f"[dolby] sitemap={len(job_urls)} job URLs")

    async with AsyncSession(impersonate="chrome124") as session:

        sem     = asyncio.Semaphore(10)
        results = await asyncio.gather(*[_fetch_job(session, u, sem) for u in job_urls])

    jobs = [j for j in results if j]

    print(f"[dolby] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape())
    for j in jobs[:5]:
        print(j["title"], "|", j["location"], "|", j["posted_date"])
    print(f"Total: {len(jobs)}")

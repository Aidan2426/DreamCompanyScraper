import asyncio
import json
import re
import html as html_lib
from datetime import datetime
from curl_cffi.requests import AsyncSession

BASE         = "https://www.workatastartup.com"
ALGOLIA_APP  = "45BWZJ1SGC"
ALGOLIA_URL  = f"https://{ALGOLIA_APP}-dsn.algolia.net/1/indexes/*/queries"


def _fmt_date(s: str) -> str:
    if not s:
        return ""
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).strftime("%b %d, %Y")
    except Exception:
        return ""


def _parse_page_json(html_text: str) -> dict:
    """Extract and decode the data-page JSON from an Inertia page."""
    m = re.search(r'<div[^>]+data-page="([^"]*)"', html_text, re.DOTALL)
    if not m:
        return {}
    raw = html_lib.unescape(m.group(1))
    return json.loads(raw)


async def _try_algolia(session: AsyncSession, algolia_key: str) -> list[dict]:
    """Try to pull all jobs via Algolia browse API."""
    # Possible index names — try until one works
    for index in ("Job_production", "jobs_production", "waas_jobs_production", "Job"):
        try:
            r = await session.post(
                ALGOLIA_URL,
                json={"requests": [{"indexName": index, "params": "hitsPerPage=1000&page=0&attributesToRetrieve=*"}]},
                headers={
                    "X-Algolia-Application-Id": ALGOLIA_APP,
                    "X-Algolia-API-Key": algolia_key,
                    "Content-Type": "application/json",
                },
                timeout=30,
            )
            if r.status_code != 200:
                continue
            data = r.json()
            results = data.get("results", [{}])[0]
            hits = results.get("hits", [])
            if hits:
                print(f"[workatastartup] Algolia index={index} total={results.get('nbHits')} hits={len(hits)}")
                return hits, results.get("nbPages", 1), index
        except Exception as e:
            print(f"[workatastartup] Algolia {index}: {e}")
    return [], 0, ""


async def scrape() -> list[dict]:
    jobs   = []
    seen   = set()

    async with AsyncSession(impersonate="chrome124") as session:
        # Step 1: fetch homepage to grab Algolia key
        r0 = await session.get(BASE + "/jobs", timeout=30)
        r0.raise_for_status()
        html_text = r0.text

        # Extract Algolia key from window.AlgoliaOpts
        algolia_key = ""
        m = re.search(r'AlgoliaOpts\s*=\s*(\{[^}]+\})', html_text)
        if m:
            try:
                opts = json.loads(m.group(1))
                algolia_key = opts.get("key", "")
            except Exception:
                pass
        print(f"[workatastartup] Algolia key found: {bool(algolia_key)}")

        # Step 2: try Algolia first (fastest)
        raw_hits = []
        if algolia_key:
            raw_hits, nb_pages, index_name = await _try_algolia(session, algolia_key)

            # Paginate if needed
            if nb_pages > 1 and index_name:
                pages = await asyncio.gather(*[
                    session.post(
                        ALGOLIA_URL,
                        json={"requests": [{"indexName": index_name, "params": f"hitsPerPage=1000&page={p}&attributesToRetrieve=*"}]},
                        headers={"X-Algolia-Application-Id": ALGOLIA_APP, "X-Algolia-API-Key": algolia_key, "Content-Type": "application/json"},
                        timeout=30,
                    )
                    for p in range(1, nb_pages)
                ])
                for pr in pages:
                    if pr.status_code == 200:
                        raw_hits.extend(pr.json().get("results", [{}])[0].get("hits", []))

        # Step 3: if Algolia worked, parse hits
        if raw_hits:
            for j in raw_hits:
                job_id = str(j.get("id") or j.get("objectID") or "").strip()
                title  = (j.get("title") or "").strip()
                if not job_id or not title or job_id in seen:
                    continue
                seen.add(job_id)
                co = j.get("company") or {}
                co_name = (co.get("name") if isinstance(co, dict) else j.get("companyName") or j.get("company_name") or "").strip()
                jobs.append({
                    "role_id":     f"yc_{job_id}",
                    "title":       title,
                    "team":        (j.get("role_type") or j.get("roleType") or j.get("function") or "").strip(),
                    "location":    (j.get("location") or "").strip(),
                    "posted_date": _fmt_date(j.get("created_at") or j.get("createdAt") or ""),
                    "url":         j.get("url") or f"{BASE}/jobs/{job_id}",
                    "company":     co_name,
                    "experience":  "",
                })
        else:
            # Fallback: scrape HTML pages
            print("[workatastartup] Algolia failed — falling back to HTML scraping")
            page = 1
            while True:
                r = await session.get(f"{BASE}/jobs", params={"page": page}, timeout=30)
                if not r.ok:
                    break
                data   = _parse_page_json(r.text)
                props  = data.get("props", {})
                pjobs  = props.get("jobs") or []
                if not pjobs:
                    break
                print(f"[workatastartup] HTML page={page} jobs={len(pjobs)}")
                for j in pjobs:
                    job_id = str(j.get("id", "")).strip()
                    title  = (j.get("title") or "").strip()
                    if not job_id or not title or job_id in seen:
                        continue
                    seen.add(job_id)
                    jobs.append({
                        "role_id":     f"yc_{job_id}",
                        "title":       title,
                        "team":        (j.get("roleType") or "").strip(),
                        "location":    (j.get("location") or "").strip(),
                        "posted_date": "",
                        "url":         f"{BASE}/jobs/{job_id}",
                        "company":     (j.get("companyName") or "").strip(),
                        "experience":  "",
                    })
                # stop if fewer than expected (last page) or no pagination signal
                if len(pjobs) < 20 or not props.get("pagination", {}).get("has_next_page"):
                    break
                page += 1

    print(f"[workatastartup] Done. {len(jobs)} jobs.")
    return jobs


if __name__ == "__main__":
    async def _debug():
        jobs = await scrape()
        for j in jobs[:5]:
            print(j["title"], "|", j["company"], "|", j["location"])
        print(f"Total: {len(jobs)}")
    asyncio.run(_debug())

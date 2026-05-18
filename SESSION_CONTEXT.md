# Session Context — Pick Up Here Next Time

Last updated: 2026-05-17

---

## What This Project Is

`DreamCompanyScraper` — async Python job scraper. Scrapes ~140 companies, stores in SQLite (`jobs.db`), outputs `jobs.json`, builds `index.html` via `build.py`. Deployed to GitHub Pages via GitHub Actions daily cron at 3am EST (8am UTC).

Live site: https://aidan2426.github.io/DreamCompanyScraper/

---

## Git State Right Now

Branch: `main`. Everything committed and pushed. Recent commits:
- `de847f5` — favorites feature (build.py: ⭐ My Companies pill + star buttons)
- `f917c0e` — bloomberg, cdpr, l3harris scrapers
- `a2f6048` — moderna, booz allen, j&j, pfizer, merck scrapers
- `7ece0dd` — aurora, datadog, 2k scrapers

**Unpushed:** Nothing known. Confirm with `git status`.

---

## What Was Built This Session

### New Scrapers (all tested, committed)

| Company | File | Platform | Jobs | Status |
|---|---|---|---|---|
| Aurora | `scrapers/aurora.py` | Algolia→Greenhouse | 165 | ✅ |
| Datadog | `scrapers/datadog.py` | Greenhouse | 409 | ✅ |
| 2K | `scrapers/twok.py` | Greenhouse | 111 | ✅ |
| Moderna | `scrapers/moderna.py` | Workday | 155 | ✅ |
| Booz Allen | `scrapers/boozallen.py` | Workday | 1847 | ✅ |
| J&J | `scrapers/jnj.py` | Workday | 1740 | ✅ |
| Pfizer | `scrapers/pfizer.py` | Workday | 535 | ✅ |
| Merck | `scrapers/merck.py` | Phenom | 287 | ✅ |
| CD Projekt Red | `scrapers/cdpr.py` | SmartRecruiters | 61 | ✅ |
| Bloomberg | `scrapers/bloomberg.py` | Avature HTML (42 pages) | 501 | ✅ |
| L3Harris | `scrapers/l3harris.py` | TalentBrew HTML (111 pages) | 1661 | ✅ |

### Frontend Feature: My Companies (Favorites)

Added to `build.py`:
- **⭐ My Companies pill** in filter bar — toggles `state.favOnly`
- **★ star button** on each company tile in Company dropdown grid
- Click ☆ → turns ★ gold, adds to `localStorage.fav_companies`
- When pill active: filters to show only favorited company jobs
- Works with all sorts (Newest, For You, A-Z) and other filters
- Count badge on pill shows how many companies are favorited
- Persists across page refreshes via localStorage

---

## main.py Current Import Line

```python
from scrapers import apple, google, microsoft, netflix, meta, amazon, openai, anthropic, disney, nvidia, hershey, ibm, cisco, oracle, universal, duolingo, hp, intel, qualcomm, micron, paramount, adobe, motorola, samsung, analogdevices, ebay, gecko, westerndigital, nps, xai, palantir, sony, nintendo, ea, epicgames, roblox, ubisoft, pinterest, linkedin, supercell, pwc, spotify, verizon, amd, salesforce, uber, airbnb, dropbox, twitch, yahoo, riotgames, fujifilm, pnc, upmc, natgeo, panasonic, snap, logitech, cloudflare, peloton, zillow, garmin, autodesk, deloitte, wesco, viatris, dsg, alcoa, arconic, westinghouse, eqt, howmet, americaneagle, coherent, nike, adidas, razer, stripe, notion, workatastartup, visa, bny, mastercard, generaldynamics, ford, sandisk, figma, capitalone, crowdstrike, boeing, wabtec, lenovo, tesla, spacex, lockheed, paypal, dell, broadcom, robopgh, aqua, cmu, covestro, fnb, bechtel, highmark, kennametal, leidos, servicenow, united, armada, bytedance, wbd, seatgeek, ticketmaster, stubhub, cgi, indeed, affirm, formenergy, gevernova, bdo, emerson, questdiagnostics, ey, fedex, gianteagle, atimaterials, ppg, gm, rivian, hubspot, github, discord, aurora, datadog, twok, moderna, boozallen, jnj, pfizer, merck, cdpr, bloomberg, l3harris
```

---

## Investigated But Blocked / Skipped This Session

| Company | Platform | Reason |
|---|---|---|
| **Northrop Grumman** | Eightfold AI | 403 on API — same as Accenture. Skip. |
| **McKinsey** | Unknown | Page times out. Workday tenant not found. |
| **American Express** | Oracle HCM | 403 Forbidden |
| **layoffs.fyi** | Airtable embed | iframe with Airtable data, server-side auth. Abandoned. |

---

## Companies Still Remaining (To Do List)

From the user's list that were NOT started:
- **Bloomberg** — ✅ Done this session
- **Square Enix** — Not investigated yet
- **CD Projekt Red** — ✅ Done this session
- **L3Harris** — ✅ Done this session
- **McKinsey** — Blocked (timeout, unknown ATS)
- **BCG** — Not investigated yet
- **MSA Safety** — Not investigated yet
- **ExlService** — Not investigated yet
- **Koppers** — Not investigated yet

From "Broke" list worth fixing:
- Databricks, Snowflake, Zoom — probably Greenhouse/Lever
- JP Morgan Chase — likely Workday
- Raytheon — defense portal
- Goldman Sachs — own portal
- Blizzard — under Microsoft/Activision now

---

## Key Technical Facts

### GitHub Actions
- File: `.github/workflows/scrape.yml`
- Cron: `0 8 * * *` UTC = 3am EST
- Caches `jobs.db` between runs (key: `jobs-db-{run_id}`, restore-keys: `jobs-db-`)
- Deploys to `dist/` folder (NOT root — peaceiris respects .gitignore)
- Manual trigger: Actions tab → "Daily Job Scrape" → Run workflow

### Platform Patterns Learned

**Greenhouse (simplest):**
```python
GET https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true
# Returns {"jobs": [...]}  — all jobs in one shot
# Fields: id, title, location.name, departments[0].name, first_published, absolute_url
```
Board names: `discord`, `hubspot`, `2k`, `datadog`, `bungie`

**Workday POST API:**
```python
POST https://{tenant}.wd*.myworkdayjobs.com/wday/cxs/{tenant}/{SITE}/jobs
body: {"limit": 20, "offset": offset, "searchText": "", "locations": []}
# Returns {"total": N, "jobPostings": [...]}
# Fields: title, externalPath (→job_id), locationsText, postedOn
# JOB_BASE = https://{tenant}.wd*.myworkdayjobs.com/en-US/{SITE}
# Max limit = 20, paginate with offset
```
Tenants: `ppg/PPG_CAREERS`, `gianteagle/GEExternalcareers`, `modernatx/M_tx`, `bah/BAH_Jobs`, `jj/JJ` (wd5), `pfizer/PfizerCareers`

**Phenom People (eagerLoadRefineSearch):**
```python
GET https://{domain}/search-results?keywords=&from=0&size={total+50}
# Data in phApp.ddo JSON embedded in HTML
# Navigate: ddo["eagerLoadRefineSearch"]["data"]["jobs"]
# Must use brace-counting JSON extractor (regex breaks on nested arrays)
# Fields: reqId, title, category, cityState, postedDate, applyUrl
```
Used for: `atimaterials`, `merck`

**Jibe/iCIMS (GitHub, Rivian):**
```python
GET https://{domain}/api/jobs?limit=50&page=1
# NOTE: use page=N NOT offset=N
# Returns {"totalCount": N, "jobs": [...]}
# Job data in entry["data"]: req_id, title, department, location_name, posted_date, slug
```

**Algolia (Aurora):**
```python
GET https://UYBO3E5EHF-dsn.algolia.net/1/indexes/Greenhouse?query=&hitsPerPage=250
headers: X-Algolia-Application-Id: UYBO3E5EHF, X-Algolia-API-Key: 7a9b56bc6afb962030d482030f588e1e
# Same Greenhouse field format
# NOTE: POST doesn't work — must use GET with query params
```

**SmartRecruiters (CD Projekt Red):**
```python
GET https://api.smartrecruiters.com/v1/companies/{SLUG}/postings?limit=100&offset=0
# Returns {"totalFound": N, "content": [...]}
# Fields: id, name, releasedDate, location{city,region,country}, department{label}
# Job URL: https://jobs.smartrecruiters.com/{SLUG}/{id}
# Public API, no auth needed
```
Slug: `CDPROJEKTRED`

**Avature HTML (Bloomberg):**
```python
GET https://bloomberg.avature.net/careers/SearchJobs/?jobRecordsPerPage=12&jobOffset={offset}
# 12 per page, 501 total = 42 pages
# Parse: <a class="link" href="...JobDetail/.../{id}">Title</a>
#        <span class="list-item-location">City, Country</span>
# IMPORTANT: Use class="link" to avoid matching "Apply" buttons (same href pattern)
```

**TalentBrew HTML (L3Harris):**
```python
GET https://careers.l3harris.com/en/search-jobs?p={page}
# 111 pages of ~15 jobs = ~1,665 total
# Parse: <a href="/en/job/{city}/{slug}/4832/{job_id}" data-job-id="...">
#          <h2>Title</h2>
#          <span class="results-facet job-category">Category</span>
#          <span class="results-facet job-location test3">City, ST</span>
#        </a>
# Total pages from: "page 1 of 111"
```

**Umbraco/server-rendered HTML (GM):**
```python
GET https://search-careers.gm.com/en/jobs/?search=&location=&page=N
# Parse HTML with regex — splits on card divs
# 42 pages
```

**Paradox.ai (FedEx):**
```python
GET https://careers.fedex.com/jobs?page_number=N&page_size=25
# NOTE: ?page=N doesn't work — must use page_number + page_size
```

### Broken/Blocked Companies
- **Accenture** — AEM/Adobe CSRF, requires JS execution. Skip.
- **LinkedIn** — In ALWAYS_SKIP set (requires auth)
- **Northrop Grumman** — Eightfold AI with CSRF/403
- **SAIC** — Cloudflare blocking
- **American Express** — Oracle HCM, 403
- **Unity** — No accessible ATS
- **Take-Two** — Client-side only
- **Bungie** — Greenhouse but 1 job only
- **McKinsey** — Page times out, ATS unknown

---

## How to Continue Next Time

1. Check git status: `git status`

2. If any untracked scrapers exist, test first:
   ```
   python main.py --company <name>
   ```

3. Next companies to investigate:
   - **Square Enix** — find their ATS
   - **BCG** — find their ATS (might be SmartRecruiters)
   - **L3Harris** — ✅ done
   - **MSA Safety** — small Pittsburgh company, easy to check
   - **Koppers** — Pittsburgh company

4. Fix broken scrapers:
   - Databricks, Snowflake, Zoom — check if still Greenhouse/Lever
   - JP Morgan Chase — try Workday variants

5. Build new scraper template (Workday pattern from ppg.py):
   ```python
   # Copy scrapers/ppg.py, change:
   API_URL  = "https://{tenant}.wd{N}.myworkdayjobs.com/wday/cxs/{tenant}/{SITE}/jobs"
   JOB_BASE = "https://{tenant}.wd{N}.myworkdayjobs.com/en-US/{SITE}"
   # Update role_id prefix and company name
   # Print statement: [companyname]
   ```

6. After adding scrapers, always wire into main.py:
   - Add to import line
   - Add to `all_scrapers` dict in `run()`
   - Test: `python main.py --company <name>`
   - Commit + push

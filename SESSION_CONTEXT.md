# Session Context — Pick Up Here Next Time

Last updated: 2026-05-16

---

## What This Project Is

`DreamCompanyScraper` — async Python job scraper. Scrapes ~130 companies, stores in SQLite (`jobs.db`), outputs `jobs.json`, builds `index.html` via `build.py`. Deployed to GitHub Pages via GitHub Actions daily cron at 3am EST (8am UTC).

Live site: https://aidan2426.github.io/DreamCompanyScraper/

---

## Git State Right Now

Branch: `main`. These files are **NOT committed yet** (untracked/staged):
- `scrapers/aurora.py` — written, NOT tested yet
- `scrapers/datadog.py` — written, NOT tested yet
- `scrapers/twok.py` — written, NOT tested yet

**Also not committed from earlier this session** (were written but user interrupted before push):
- `scrapers/rivian.py` — fixed pagination (offset→page param), tested ✓ 529 jobs
- `scrapers/hubspot.py` — tested ✓ 177 jobs
- `scrapers/github.py` — tested ✓ 100 jobs
- `scrapers/discord.py` — tested ✓ 78 jobs
- `main.py` — wired all above + aurora/datadog/twok

**Commit everything with:**
```
git add scrapers/rivian.py scrapers/hubspot.py scrapers/github.py scrapers/discord.py scrapers/aurora.py scrapers/datadog.py scrapers/twok.py main.py
git commit -m "add rivian/hubspot/github/discord/aurora/datadog/2k scrapers"
git push
```

---

## What Was In Progress When Interrupted

Building a batch of 8 new scrapers from this URL list the user gave:
- Bungie, Datadog, Moderna, Aurora, Unity, Take-Two, 2K, Northrop Grumman, Booz Allen, SAIC, AmEx, J&J, Pfizer, Merck

### Status of Each:

| Company | Platform | API | Jobs | Status |
|---|---|---|---|---|
| **2K** | Greenhouse | `boards-api.greenhouse.io/v1/boards/2k/jobs` | 111 | ✅ scraper written (`twok.py`), NOT tested |
| **Datadog** | Greenhouse | `boards-api.greenhouse.io/v1/boards/datadog/jobs` | 409 | ✅ scraper written, NOT tested |
| **Aurora** | Algolia→Greenhouse | GET `https://UYBO3E5EHF-dsn.algolia.net/1/indexes/Greenhouse?query=&hitsPerPage=250` headers: `X-Algolia-Application-Id: UYBO3E5EHF`, `X-Algolia-API-Key: 7a9b56bc6afb962030d482030f588e1e` | 165 | ✅ scraper written, NOT tested |
| **Moderna** | Workday | POST `https://modernatx.wd1.myworkdayjobs.com/wday/cxs/modernatx/M_tx/jobs` | 155 | ❌ NOT started yet |
| **Booz Allen** | Workday | POST `https://bah.wd1.myworkdayjobs.com/wday/cxs/bah/BAH_Jobs/jobs` | 1848 | ❌ NOT started yet |
| **J&J** | Workday | POST `https://jj.wd5.myworkdayjobs.com/wday/cxs/jj/JJ/jobs` | 1757 | ❌ NOT started yet |
| **Pfizer** | Workday | POST `https://pfizer.wd1.myworkdayjobs.com/wday/cxs/pfizer/PfizerCareers/jobs` | 539 | ❌ NOT started yet |
| **Merck** | Phenom | GET `https://jobs.merck.com/us/en/search-results?keywords=&from=0&size=350` | 294 | ❌ NOT started yet |
| **Northrop Grumman** | Eightfold | BLOCKED — CSRF, same as Accenture | ~800 | ⛔ Skip |
| **SAIC** | Unknown | Cloudflare blocking all requests (5254b response) | ? | ⛔ Skip |
| **American Express** | Oracle HCM | `egug.fa.us2.oraclecloud.com` — complex auth | ? | ⛔ Skip |
| **Unity** | Unknown | No ATS found. Lever=2 jobs, GH=0, Workday=none match | ? | ⛔ Skip |
| **Take-Two** | Contentful (client-side) | Bails to CSR, no API endpoint, images-only CDN | ? | ⛔ Skip |
| **Bungie** | Greenhouse | `boards-api.greenhouse.io/v1/boards/bungie/jobs` | **1 job** | ⛔ Skip (not worth it) |

### Workday Scraper Pattern (copy from `scrapers/ppg.py`)
All 4 Workday ones (Moderna, Booz Allen, J&J, Pfizer) follow the exact same pattern as `ppg.py`:
- POST with `{"limit": 20, "offset": offset, "searchText": "", "locations": []}`
- Response: `{"total": N, "jobPostings": [...]}`
- Each posting: `externalPath` → `job_id`, `title`, `locationsText`, `postedOn`
- JOB_BASE = `https://{tenant}.wd*.myworkdayjobs.com/en-US/{SITE}`
- Note: `limit: 100` doesn't work — max is 20

### Merck Phenom Pattern (copy from `scrapers/atimaterials.py`)
- GET `https://jobs.merck.com/us/en/search-results?keywords=&from=0&size=350`
- Data in `phApp.ddo = {...}` → `eagerLoadRefineSearch.data.jobs` (294 jobs)
- Use brace-counting `_extract_json()` — regex fails on nested arrays
- Fields: `reqId`, `title`, `category` (team), `cityState` (loc), `postedDate`, `applyUrl`

---

## main.py Current Import Line

```python
from scrapers import apple, google, microsoft, netflix, meta, amazon, openai, anthropic, disney, nvidia, hershey, ibm, cisco, oracle, universal, duolingo, hp, intel, qualcomm, micron, paramount, adobe, motorola, samsung, analogdevices, ebay, gecko, westerndigital, nps, xai, palantir, sony, nintendo, ea, epicgames, roblox, ubisoft, pinterest, linkedin, supercell, pwc, spotify, verizon, amd, salesforce, uber, airbnb, dropbox, twitch, yahoo, riotgames, fujifilm, pnc, upmc, natgeo, panasonic, snap, logitech, cloudflare, peloton, zillow, garmin, autodesk, deloitte, wesco, viatris, dsg, alcoa, arconic, westinghouse, eqt, howmet, americaneagle, coherent, nike, adidas, razer, stripe, notion, workatastartup, visa, bny, mastercard, generaldynamics, ford, sandisk, figma, capitalone, crowdstrike, boeing, wabtec, lenovo, tesla, spacex, lockheed, paypal, dell, broadcom, robopgh, aqua, cmu, covestro, fnb, bechtel, highmark, kennametal, leidos, servicenow, united, armada, bytedance, wbd, seatgeek, ticketmaster, stubhub, cgi, indeed, affirm, formenergy, gevernova, bdo, emerson, questdiagnostics, ey, fedex, gianteagle, atimaterials, ppg, gm, rivian, hubspot, github, discord
```

**Still need to add to main.py:** `aurora`, `datadog`, `twok`, and all the NOT-started ones once built.

The `all_scrapers` dict in `run()` also needs matching entries — same pattern, just `"aurora": aurora` etc.

---

## Companies Still Remaining (To Do List)

From the user's list, these need scrapers built:
- **Moderna** — Workday, 155 jobs ← build next
- **Booz Allen** — Workday, 1848 jobs ← build next
- **J&J** — Workday, 1757 jobs ← build next
- **Pfizer** — Workday, 539 jobs ← build next
- **Merck** — Phenom, 294 jobs ← build next
- Bloomberg
- Square Enix
- CD Projekt Red
- L3Harris
- McKinsey
- BCG
- MSA Safety
- ExlService
- Koppers
- Moderna (done above)
- American Express (blocked: Oracle HCM)
- Northrop Grumman (blocked: Eightfold)
- SAIC (blocked: CF)
- Unity (blocked: no ATS found)
- Take-Two (blocked: CSR only)

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
Board names used: `discord`, `hubspot`, `2k`, `datadog`

**Workday POST API:**
```python
POST https://{tenant}.wd*.myworkdayjobs.com/wday/cxs/{tenant}/{SITE}/jobs
body: {"limit": 20, "offset": offset, "searchText": "", "locations": []}
# Returns {"total": N, "jobPostings": [...]}
# Fields: title, externalPath (→job_id), locationsText, postedOn
# JOB_BASE = https://{tenant}.wd*.myworkdayjobs.com/en-US/{SITE}
# Max limit = 20, paginate with offset
```
Tenants used: `ppg/PPG_CAREERS`, `gianteagle/GEExternalcareers`, `modernatx/M_tx`, `bah/BAH_Jobs`, `jj/JJ`, `pfizer/PfizerCareers`

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
# NOTE: use page=N NOT offset=N (offset silently returns same 50 jobs every time)
# Returns {"totalCount": N, "jobs": [...]}
# Job data in entry["data"]: req_id, title, department, location_name, posted_date, slug
```

**Algolia (Aurora):**
```python
GET https://UYBO3E5EHF-dsn.algolia.net/1/indexes/Greenhouse?query=&hitsPerPage=250
headers: X-Algolia-Application-Id, X-Algolia-API-Key
# Same Greenhouse field format: id, title, location.name, departments, first_published, absolute_url
# NOTE: POST doesn't work — must use GET with query params
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
- **Northrop Grumman** — Eightfold AI with CSRF
- **SAIC** — Cloudflare blocking
- **American Express** — Oracle HCM
- **Unity** — No accessible ATS
- **Take-Two** — Client-side only
- **Bungie** — Greenhouse but 1 job only

---

## How to Continue Tomorrow

1. Test the 3 untracked scrapers first:
```
python main.py --company aurora datadog twok
```

2. If those pass, commit everything:
```
git add scrapers/rivian.py scrapers/hubspot.py scrapers/github.py scrapers/discord.py scrapers/aurora.py scrapers/datadog.py scrapers/twok.py main.py
git commit -m "add rivian/hubspot/github/discord/aurora/datadog/2k scrapers"
git push
```

3. Build the 5 remaining confirmed scrapers:
   - `scrapers/moderna.py` — copy ppg.py pattern, API: `modernatx.wd1.myworkdayjobs.com/wday/cxs/modernatx/M_tx/jobs`, company="Moderna", JOB_BASE=`https://modernatx.wd1.myworkdayjobs.com/en-US/M_tx`
   - `scrapers/boozallen.py` — Workday, `bah.wd1.myworkdayjobs.com/wday/cxs/bah/BAH_Jobs/jobs`, company="Booz Allen Hamilton"
   - `scrapers/jnj.py` — Workday, `jj.wd5.myworkdayjobs.com/wday/cxs/jj/JJ/jobs`, company="Johnson & Johnson"
   - `scrapers/pfizer.py` — Workday, `pfizer.wd1.myworkdayjobs.com/wday/cxs/pfizer/PfizerCareers/jobs`, company="Pfizer"
   - `scrapers/merck.py` — Phenom, `jobs.merck.com/us/en/search-results`, copy atimaterials.py pattern, company="Merck"

4. Add all to main.py imports and all_scrapers dict

5. Test with `python main.py --company moderna boozallen jnj pfizer merck`

6. After that, user may want: Bloomberg, Square Enix, L3Harris, McKinsey, BCG, and fixing Databricks/Snowflake/JPMorgan from the broke list.

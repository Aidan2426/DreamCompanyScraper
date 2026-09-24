"""
Reads jobs.json and generates index.html.
Run: python build.py
"""
import argparse
import json
import os
import re
import shutil
import time
import urllib.request
import urllib.parse
import webbrowser

_parser = argparse.ArgumentParser()
_parser.add_argument("--no-open", action="store_true")
_args = _parser.parse_args()

def _gfav(domain):
    return f"https://www.google.com/s2/favicons?domain={domain}&sz=128"

COMPANY_LOGOS = {
    "Apple":                     _gfav("apple.com"),
    "Google":                    _gfav("google.com"),
    "Microsoft":                 _gfav("microsoft.com"),
    "Netflix":                   _gfav("netflix.com"),
    "Meta":                      _gfav("meta.com"),
    "Amazon":                    _gfav("amazon.com"),
    "OpenAI":                    _gfav("openai.com"),
    "Anthropic":                 _gfav("anthropic.com"),
    "Analog Devices":            _gfav("analog.com"),
    "Pinterest":                 _gfav("pinterest.com"),
    "LinkedIn":                  _gfav("linkedin.com"),
    "Supercell":                 _gfav("supercell.com"),
    "PwC":                       _gfav("pwc.com"),
    "Spotify":                   _gfav("spotify.com"),
    "Verizon":                   _gfav("verizon.com"),
    "AMD":                       _gfav("amd.com"),
    "Salesforce":                _gfav("salesforce.com"),
    "Uber":                      _gfav("uber.com"),
    "Airbnb":                    _gfav("airbnb.com"),
    "Dropbox":                   _gfav("dropbox.com"),
    "Twitch":                    _gfav("twitch.tv"),
    "Yahoo":                     _gfav("yahoo.com"),
    "Riot Games":                _gfav("riotgames.com"),
    "Fujifilm":                  _gfav("fujifilm.com"),
    "PNC":                       _gfav("pnc.com"),
    "UPMC":                      _gfav("upmc.com"),
    "National Geographic Society": _gfav("nationalgeographic.com"),
    "Panasonic":                 _gfav("panasonic.com"),
    "Snap":                      _gfav("snap.com"),
    "Logitech":                  _gfav("logitech.com"),
    "Cloudflare":                _gfav("cloudflare.com"),
    "Peloton":                   _gfav("onepeloton.com"),
    "Zillow":                    _gfav("zillow.com"),
    "Garmin":                    _gfav("garmin.com"),
    "Autodesk":                  _gfav("autodesk.com"),
    "Deloitte":                  _gfav("deloitte.com"),
    "Wesco":                     _gfav("wesco.com"),
    "Viatris":                   _gfav("viatris.com"),
    "Dick's Sporting Goods":     _gfav("dickssportinggoods.com"),
    "Alcoa":                     _gfav("alcoa.com"),
    "Arconic":                   _gfav("arconic.com"),
    "Westinghouse":              _gfav("westinghousenuclear.com"),
    "EQT":                       _gfav("eqt.com"),
    "Howmet Aerospace":          _gfav("howmet.com"),
    "American Eagle":            _gfav("ae.com"),
    "Coherent":                  _gfav("coherent.com"),
    "Nike":                      _gfav("nike.com"),
    "Adidas":                    _gfav("adidas.com"),
    "Razer":                     _gfav("razer.com"),
    "Stripe":                    _gfav("stripe.com"),
    "Notion":                    _gfav("notion.so"),
    "Visa":                      _gfav("visa.com"),
    "BNY":                       _gfav("bny.com"),
    "Mastercard":                _gfav("mastercard.com"),
    "General Dynamics":          _gfav("gd.com"),
    "Ford":                      _gfav("ford.com"),
    "Sandisk":                   _gfav("sandisk.com"),
    "Figma":                     _gfav("figma.com"),
    "Capital One":               _gfav("capitalone.com"),
    "CrowdStrike":               _gfav("crowdstrike.com"),
    "Boeing":                    _gfav("boeing.com"),
    "Wabtec":                    _gfav("wabtec.com"),
    "Lenovo":                    _gfav("lenovo.com"),
    "Tesla":                     _gfav("tesla.com"),
    "SpaceX":                    _gfav("spacex.com"),
    "Lockheed Martin":           _gfav("lockheedmartin.com"),
    "PayPal":                    _gfav("paypal.com"),
    "Dell":                      _gfav("dell.com"),
    "Broadcom":                  _gfav("broadcom.com"),
    "Disney":                    _gfav("disney.com"),
    "Nvidia":                    _gfav("nvidia.com"),
    "Hershey":                   _gfav("thehersheycompany.com"),
    "IBM":                       _gfav("ibm.com"),
    "Cisco":                     _gfav("cisco.com"),
    "Oracle":                    _gfav("oracle.com"),
    "Universal Parks & Resorts": _gfav("universalparks.com"),
    "Duolingo":                  _gfav("duolingo.com"),
    "HP":                        _gfav("hp.com"),
    "Intel":                     _gfav("intel.com"),
    "Qualcomm":                  _gfav("qualcomm.com"),
    "Micron":                    _gfav("micron.com"),
    "Paramount":                 _gfav("paramount.com"),
    "Adobe":                     _gfav("adobe.com"),
    "Motorola Solutions":        _gfav("motorolasolutions.com"),
    "Samsung":                   _gfav("samsung.com"),
    "eBay":                      _gfav("ebay.com"),
    "Gecko Robotics":            _gfav("geckorobotics.com"),
    "Western Digital":           _gfav("westerndigital.com"),
    "National Park Service":     _gfav("nps.gov"),
    "xAI":                       _gfav("x.ai"),
    "Palantir":                  _gfav("palantir.com"),
    "Sony":                      _gfav("sony.com"),
    "Nintendo":                  _gfav("nintendo.com"),
    "EA":                        _gfav("ea.com"),
    "Epic Games":                _gfav("epicgames.com"),
    "Roblox":                    _gfav("roblox.com"),
    "Ubisoft":                   _gfav("ubisoft.com"),
    "RoboPGH":                   _gfav("robopgh.org"),
    "Aqua":                      _gfav("aquawater.com"),
    "CMU":                       _gfav("cmu.edu"),
    "Covestro":                  _gfav("covestro.com"),
    "First National Bank":       _gfav("fnb-corp.com"),
    "Bechtel":                   _gfav("bechtel.com"),
    "Highmark Health":           _gfav("highmarkhealth.org"),
    "Kennametal":                _gfav("kennametal.com"),
    "Leidos":                    _gfav("leidos.com"),
    "ServiceNow":                _gfav("servicenow.com"),
    "United Airlines":           _gfav("united.com"),
    "Armada":                    _gfav("armada.com"),
    "ByteDance":                 _gfav("bytedance.com"),
    "Warner Bros. Discovery":    _gfav("wbd.com"),
    "SeatGeek":                  _gfav("seatgeek.com"),
    "Ticketmaster":              _gfav("ticketmaster.com"),
    "StubHub":                   _gfav("stubhub.com"),
    "CGI":                       _gfav("cgi.com"),
    # RoboPGH employer companies
    "ANKI":                      _gfav("anki.com"),
    "Advanced Construction Robotics": _gfav("acrbotics.com"),
    "Aethon":                    _gfav("aethon.com"),
    "Agility Robotics":          _gfav("agilityrobotics.com"),
    "Allvision":                 _gfav("allvision.io"),
    "Astrobotic":                _gfav("astrobotic.com"),
    "Aurora":                    _gfav("aurora.tech"),
    "BEA Sensors":               _gfav("beasensors.com"),
    "Bosch":                     _gfav("bosch.com"),
    "CapSen Robotics":           _gfav("capsenrobotics.com"),
    "Carnegie Robotics":         _gfav("carnegierobotics.com"),
    "Caterpillar":               _gfav("caterpillar.com"),
    "ESTAT Actuation":           _gfav("estatactuation.com"),
    "Edge Case Research":        _gfav("edgecaseresearch.com"),
    "Eye-Bot Aerial Solutions":  _gfav("eye-bot.com"),
    "Formant":                   _gfav("formant.io"),
    "Fort Robotics":             _gfav("fortrobotics.com"),
    "FuturHand Robotics":        _gfav("futurhand.com"),
    "Gather AI":                 _gfav("gather.ai"),
    "Hellbender":                _gfav("hellbenderindustries.com"),
    "Hitachi":                   _gfav("hitachi.com"),
    "Identified Technologies":   _gfav("identifiedtechnologies.com"),
    "KEF Robotics":              _gfav("kefrobotics.com"),
    "Latitude AI":               _gfav("lat.ai"),
    "Matthews International":    _gfav("matthewsinternational.com"),
    "Mine Vision Systems":       _gfav("minevision.ai"),
    "Motional":                  _gfav("motional.com"),
    "NREC":                      _gfav("nrec.ri.cmu.edu"),
    "Near Earth Autonomy":       _gfav("nearearthautonomy.com"),
    "Neuraville":                _gfav("neuraville.com"),
    "Omnicell":                  _gfav("omnicell.com"),
    "Onward Robotics":           _gfav("onwardrobotics.com"),
    "Palladyne AI":              _gfav("palladyne.ai"),
    "Phlux Technologies":        _gfav("phlux.com"),
    "Pittsburgh Robotics Network": _gfav("robopgh.org"),
    "ProtoInnovations":          _gfav("protoinnovations.com"),
    "Qeexo, Co.":               _gfav("qeexo.com"),
    "Smith &amp; Nephew":        _gfav("smith-nephew.com"),
    "Stack AV":                  _gfav("stackav.com"),
    "Waymo":                     _gfav("waymo.com"),
    "iotaMotion":                _gfav("iotamotion.com"),
    # Additional companies
    "Affirm":                    _gfav("affirm.com"),
    "ATI Materials":             _gfav("atimaterials.com"),
    "Aurora Innovation":         _gfav("aurora.tech"),
    "BDO USA":                   _gfav("bdo.com"),
    "Bloomberg":                 _gfav("bloomberg.com"),
    "Booz Allen Hamilton":       _gfav("boozallen.com"),
    "Brex":                      _gfav("brex.com"),
    "CD Projekt Red":            _gfav("cdprojektred.com"),
    "Datadog":                   _gfav("datadoghq.com"),
    "Discord":                   _gfav("discord.com"),
    "DoorDash":                  _gfav("doordash.com"),
    "EY":                        _gfav("ey.com"),
    "Elastic":                   _gfav("elastic.co"),
    "Emerson":                   _gfav("emerson.com"),
    "FedEx":                     _gfav("fedex.com"),
    "Form Energy":               _gfav("formenergy.com"),
    "GE Vernova":                _gfav("gevernova.com"),
    "General Motors":            _gfav("gm.com"),
    "Giant Eagle":               _gfav("gianteagle.com"),
    "GitHub":                    _gfav("github.com"),
    "HubSpot":                   _gfav("hubspot.com"),
    "Indeed":                    _gfav("indeed.com"),
    "Instacart":                 _gfav("instacart.com"),
    "Johnson & Johnson":         _gfav("jnj.com"),
    "L3Harris":                  _gfav("l3harris.com"),
    "Lyft":                      _gfav("lyft.com"),
    "Merck":                     _gfav("merck.com"),
    "Moderna":                   _gfav("modernatx.com"),
    "MongoDB":                   _gfav("mongodb.com"),
    "Okta":                      _gfav("okta.com"),
    "PPG Industries":            _gfav("ppg.com"),
    "Palo Alto Networks":        _gfav("paloaltonetworks.com"),
    "Pfizer":                    _gfav("pfizer.com"),
    "Planet Labs":               _gfav("planet.com"),
    "Quest Diagnostics":         _gfav("questdiagnostics.com"),
    "Reddit":                    _gfav("reddit.com"),
    "Rivian":                    _gfav("rivian.com"),
    "Robinhood":                 _gfav("robinhood.com"),
    "Twilio":                    _gfav("twilio.com"),
    "UiPath":                    _gfav("uipath.com"),
    "Vercel":                    _gfav("vercel.com"),
    "Zeta Global":               _gfav("zetaglobal.com"),
    "Zscaler":                   _gfav("zscaler.com"),
    "2K Games":                  _gfav("2k.com"),
    "monday.com":                _gfav("monday.com"),
    "Dolby":                     _gfav("dolby.com"),
}

TEAM_COLORS = {
    "Machine Learning and AI":    ("#1a3a8f", "#e8f0fe"),
    "Software and Services":      ("#0a5c2e", "#e6f9ee"),
    "Hardware":                   ("#7a2d00", "#fff0e6"),
    "Apple Retail":               ("#5c0a5c", "#f9e6f9"),
    "Operations and Supply Chain":("#4a4a00", "#f9f9e6"),
}

STATE_ABBREV = {
    "Alabama":"AL","Alaska":"AK","Arizona":"AZ","Arkansas":"AR","California":"CA",
    "Colorado":"CO","Connecticut":"CT","Delaware":"DE","Florida":"FL","Georgia":"GA",
    "Hawaii":"HI","Idaho":"ID","Illinois":"IL","Indiana":"IN","Iowa":"IA","Kansas":"KS",
    "Kentucky":"KY","Louisiana":"LA","Maine":"ME","Maryland":"MD","Massachusetts":"MA",
    "Michigan":"MI","Minnesota":"MN","Mississippi":"MS","Missouri":"MO","Montana":"MT",
    "Nebraska":"NE","Nevada":"NV","New Hampshire":"NH","New Jersey":"NJ","New Mexico":"NM",
    "New York":"NY","North Carolina":"NC","North Dakota":"ND","Ohio":"OH","Oklahoma":"OK",
    "Oregon":"OR","Pennsylvania":"PA","Rhode Island":"RI","South Carolina":"SC",
    "South Dakota":"SD","Tennessee":"TN","Texas":"TX","Utah":"UT","Vermont":"VT",
    "Virginia":"VA","Washington":"WA","West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY",
    "District of Columbia":"DC","Puerto Rico":"PR","Guam":"GU","Virgin Islands":"VI",
}

_US_ST = set(STATE_ABBREV.values())
_INTL_HINTS = {
    'bangalore','bengaluru','hyderabad','mumbai','delhi','new delhi','pune','chennai',
    'kolkata','noida','gurgaon','gurugram','ahmedabad','kochi','jaipur','indore','nagpur',
    'toronto','vancouver','montreal','ottawa','calgary','edmonton','winnipeg','halifax',
    'london','manchester','edinburgh','bristol','leeds','birmingham','glasgow','dublin',
    'amsterdam','berlin','munich','frankfurt','hamburg','cologne','stuttgart','paris',
    'lyon','marseille','madrid','barcelona','seville','milan','rome','turin','naples',
    'sydney','melbourne','brisbane','perth','adelaide','auckland','wellington','christchurch',
    'singapore','tokyo','osaka','kyoto','sapporo','beijing','shanghai','shenzhen',
    'guangzhou','hong kong','seoul','busan','taipei','kaohsiung','bangkok','jakarta',
    'kuala lumpur','manila','ho chi minh','hanoi','tel aviv','jerusalem','dubai',
    'abu dhabi','riyadh','doha','cairo','nairobi','lagos','johannesburg','cape town',
    'mexico city','guadalajara','monterrey','bogota','lima','santiago','sao paulo',
    'rio de janeiro','buenos aires','stockholm','oslo','copenhagen','helsinki',
    'zurich','geneva','bern','brussels','antwerp','vienna','warsaw','prague',
    'budapest','bucharest','athens','lisbon','porto',
}

def _extract_job_us_cities(jobs):
    counts = {}
    for j in jobs:
        loc = (j.get('location') or '').strip()
        if not loc:
            continue
        for part in re.split(r'\r?\n', loc):
            part = part.strip()
            if not part:
                continue
            m = re.match(r'^([A-Z]{2})\s*[-–]\s*(.+?)(?:\s*\(\d+\))?$', part)
            if m and m.group(1) in _US_ST and m.group(2).strip().lower() not in _INTL_HINTS:
                key = f"{m.group(2).strip()}, {m.group(1)}"
                counts[key] = counts.get(key, 0) + 1
                continue
            clean = re.sub(r'\b\d{5}(-\d{4})?\b', '', part).strip()
            segs = [s.strip() for s in clean.split(',') if s.strip()]
            if not segs:
                continue
            city = segs[0]
            city_lc = city.lower()
            if city_lc in _INTL_HINTS:
                continue
            matched = False
            for seg in segs[1:]:
                if seg in _US_ST:
                    key = f"{city}, {seg}"
                    counts[key] = counts.get(key, 0) + 1
                    matched = True
                    break
                if seg in STATE_ABBREV:
                    key = f"{city}, {STATE_ABBREV[seg]}"
                    counts[key] = counts.get(key, 0) + 1
                    matched = True
                    break
            if not matched:
                m2 = re.match(r'^(.+?)\s+([A-Z]{2})$', city)
                if m2 and m2.group(2) in _US_ST and m2.group(1).lower() not in _INTL_HINTS:
                    key = f"{m2.group(1)}, {m2.group(2)}"
                    counts[key] = counts.get(key, 0) + 1
    return counts

def _geocode_cities(city_counts, cache_file='city_coords.json', max_new=150):
    cache = {}
    if os.path.exists(cache_file):
        with open(cache_file, encoding='utf-8') as f:
            try:
                cache = json.load(f)
            except Exception:
                pass
    all_new = [c for c in city_counts if c not in cache]
    to_geocode = all_new[:max_new]
    deferred = len(all_new) - len(to_geocode)
    if to_geocode:
        print(f"Geocoding {len(to_geocode)} new cities...")
        for i, city in enumerate(to_geocode):
            try:
                q = urllib.parse.urlencode({'q': city + ', USA', 'format': 'json', 'limit': 1})
                req = urllib.request.Request(
                    f'https://nominatim.openstreetmap.org/search?{q}',
                    headers={'User-Agent': 'DreamCompanyScraper/1.0 (aash3@hawk.illinoistech.edu)'}
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read())
                if data:
                    lat, lon = float(data[0]['lat']), float(data[0]['lon'])
                    cache[city] = {'lat': lat, 'lon': lon}
                    print(f"  [{i+1}/{len(to_geocode)}] {city} -> {lat:.4f}, {lon:.4f}")
                else:
                    cache[city] = None
                    print(f"  [{i+1}/{len(to_geocode)}] {city} -> not found")
            except Exception as e:
                print(f"  [{i+1}/{len(to_geocode)}] {city} -> ERROR: {e}")
                cache[city] = None
            if i < len(to_geocode) - 1:
                time.sleep(1.1)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
        resolved = sum(1 for v in cache.values() if v)
        print(f"Geocoding done — {resolved} cities resolved.")
    if deferred:
        print(f"{deferred} new cities deferred to next run (max_new={max_new} cap).")
    return {k: v for k, v in cache.items() if v is not None}

jobs_data = {"scraped_at": "", "jobs": []}
if os.path.exists("jobs.json"):
    with open("jobs.json", encoding="utf-8") as f:
        jobs_data = json.load(f)

jobs       = jobs_data.get("jobs", [])
scraped_at = jobs_data.get("scraped_at", "")
new_count  = sum(1 for j in jobs if j.get("is_new"))
teams      = sorted({j["team"] for j in jobs if j.get("team")})
companies  = sorted({j["company"] for j in jobs if j.get("company")})
experiences = sorted({
    j["experience"] for j in jobs
    if j.get("experience") and not re.search(r'[\$]|\bGS-\d|\b\d{4,}\b', j["experience"])
})

city_counts  = _extract_job_us_cities(jobs)
city_counts  = {c: n for c, n in city_counts.items() if n >= 2}
# Geocode at most MAX_NEW_GEOCODE new cities per build (bounded to ~3min at
# 1.1s/call) so a large backlog of unresolved cities can't blow the CI job's
# timeout. Any cities beyond the cap stay uncached and get picked up on a
# later run once this file's results are committed back to the repo.
MAX_NEW_GEOCODE = 150
city_coords = _geocode_cities(city_counts, max_new=MAX_NEW_GEOCODE)

_JOB_FIELDS = ('role_id', 'title', 'team', 'location', 'posted_date', 'url',
               'company', 'first_seen', 'last_seen', 'is_new', 'experience')
# Low-cardinality fields: store each distinct value once plus an index per job.
_DICT_FIELDS = {'team', 'location', 'posted_date', 'company', 'first_seen', 'last_seen', 'experience'}

def _columnar(jobs):
    # One array per field instead of one object per job, so key names aren't
    # repeated 200k+ times; roughly halves the payload. Decoded back into job
    # objects by decodeJobs() in the page.
    out = {'n': len(jobs)}
    for k in _JOB_FIELDS:
        vals = [j.get(k) for j in jobs]
        if k in _DICT_FIELDS:
            index = {}
            out[k] = {'d': None, 'i': [index.setdefault(v, len(index)) for v in vals]}
            out[k]['d'] = list(index)
        elif k == 'is_new':
            out[k] = [1 if v else 0 for v in vals]
        else:
            out[k] = vals
    return out

def _dump_compact(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':'))

# Only jobs still listed are embedded in the page; archived ones (no longer on the
# company's site) go to archive/YYYY-MM.json by first_seen month, fetched only when
# the Archive tab (or a saved/applied job that's been archived) needs them. Keeps
# every file far under GitHub's 100 MB limit as history grows.
active_jobs   = [j for j in jobs if not j.get("archived")]
archived_jobs = [j for j in jobs if j.get("archived")]

ARCHIVE_DIR = "archive"
shutil.rmtree(ARCHIVE_DIR, ignore_errors=True)
os.makedirs(ARCHIVE_DIR)
_by_month = {}
for j in archived_jobs:
    _by_month.setdefault((j.get("first_seen") or "unknown")[:7], []).append(j)
archive_months = []
for month in sorted(_by_month, reverse=True):
    with open(os.path.join(ARCHIVE_DIR, f"{month}.json"), "w", encoding="utf-8") as f:
        f.write(_dump_compact(_columnar(_by_month[month])))
    archive_months.append({"month": month, "count": len(_by_month[month])})

# Embedded in a <script type="application/json"> block and read with JSON.parse:
# faster than V8 parsing a huge object literal, and unlike a JS string literal it
# needs no quote escaping (which added ~9 MB). Escape "</" so a URL/title can't
# close the surrounding <script> tag.
jobs_json_embed     = _dump_compact(_columnar(active_jobs)).replace('</', '<\\/')
archive_months_json = json.dumps(archive_months)
teams_json        = json.dumps(teams,        ensure_ascii=False)
companies_json    = json.dumps(companies,    ensure_ascii=False)
experiences_json  = json.dumps(experiences,  ensure_ascii=False)
state_abbrev_json = json.dumps(STATE_ABBREV, ensure_ascii=False)
logos_json        = json.dumps(COMPANY_LOGOS, ensure_ascii=False)
city_coords_json  = json.dumps(city_coords,  ensure_ascii=False)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Dream Companies</title>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⭐</text></svg>"/>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --blue:   #0071e3;
      --bg:     #f5f5f7;
      --white:  #ffffff;
      --near-black: #1d1d1f;
      --muted:  #6e6e73;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg); color: var(--near-black); min-height: 100vh;
    }}

    /* ── Hero ── */
    .hero {{
      background: #000; color: #fff;
      padding: 64px 28px 48px; text-align: center;
      display: flex; flex-direction: column; align-items: center; gap: 12px;
    }}
    .hero h1 {{
      font-size: clamp(40px, 6vw, 64px); font-weight: 700;
      letter-spacing: -1px; line-height: 1.05;
    }}
    .hero p {{ font-size: 17px; color: rgba(255,255,255,0.55); }}

    /* ── Controls ── */
    .controls-bar {{
      position: sticky; top: 0; z-index: 90;
      background: #0e0e10;
      border-bottom: 1px solid rgba(255,255,255,0.07);
      padding: 14px 24px 12px;
      display: flex; flex-direction: column;
      align-items: center; gap: 11px;
    }}
    .search-wrap {{
      position: relative; width: 100%; max-width: 580px;
    }}
    .search-wrap .s-icon {{
      position: absolute; left: 13px; top: 50%; transform: translateY(-50%);
      width: 15px; height: 15px; pointer-events: none;
      stroke: rgba(255,255,255,0.3); fill: none;
      stroke-width: 2; stroke-linecap: round; stroke-linejoin: round;
    }}
    .search-input {{
      width: 100%; height: 38px;
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.10);
      border-radius: 10px;
      padding: 0 14px 0 38px;
      font-size: 14px; color: #fff; outline: none;
      transition: border-color 0.15s, background 0.15s;
    }}
    .search-input::placeholder {{ color: rgba(255,255,255,0.3); }}
    .search-input:focus {{ background: rgba(255,255,255,0.09); border-color: rgba(0,113,227,0.65); }}
    .filter-strip {{
      display: flex; align-items: center; gap: 7px;
      flex-wrap: wrap; justify-content: center;
    }}
    .fsep {{
      width: 1px; height: 18px;
      background: rgba(255,255,255,0.12);
      flex-shrink: 0; margin: 0 3px;
    }}
    .pill {{
      font-size: 12.5px; padding: 5px 13px;
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.10);
      border-radius: 980px; color: rgba(255,255,255,0.55);
      cursor: pointer; white-space: nowrap; font-weight: 500;
      transition: all 0.15s;
    }}
    .pill:hover {{ background: rgba(255,255,255,0.11); color: #fff; border-color: rgba(255,255,255,0.2); }}
    .pill.active {{ background: var(--blue); border-color: var(--blue); color: #fff; }}
    .filter-select {{
      font-size: 12.5px; padding: 5px 26px 5px 12px;
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.10);
      border-radius: 980px; color: rgba(255,255,255,0.55);
      cursor: pointer; outline: none; appearance: none; font-weight: 500;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M1 1l4 4 4-4' stroke='rgba(255,255,255,0.4)' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
      background-repeat: no-repeat; background-position: right 9px center;
      transition: all 0.15s;
    }}
    .filter-select option {{ background: #111113; }}
    .filter-select:hover {{ color: #fff; border-color: rgba(255,255,255,0.2); background-color: rgba(255,255,255,0.10); }}
    .filter-select.active {{ border-color: var(--blue); color: #fff; background-color: rgba(0,113,227,0.18); }}

    /* ── Custom multi-select dropdowns ── */
    .custom-select {{ position: relative; }}
    .cs-btn {{
      display: inline-flex; align-items: center; gap: 6px;
      font-size: 12.5px; padding: 5px 12px;
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.10);
      border-radius: 980px; color: rgba(255,255,255,0.55);
      cursor: pointer; white-space: nowrap; font-weight: 500;
      transition: all 0.15s; user-select: none;
    }}
    .cs-btn:hover {{ background: rgba(255,255,255,0.11); color: #fff; border-color: rgba(255,255,255,0.2); }}
    .cs-btn.active {{ border-color: var(--blue); color: #fff; background: rgba(0,113,227,0.18); }}
    .cs-badge {{
      display: none; background: var(--blue); color: #fff;
      border-radius: 980px; font-size: 10px; font-weight: 700;
      padding: 1px 6px; line-height: 1.5;
    }}
    .cs-chevron {{ flex-shrink: 0; transition: transform 0.15s; }}
    .custom-select.open .cs-chevron {{ transform: rotate(180deg); }}
    .cs-panel {{
      position: absolute; top: calc(100% + 6px); left: 50%;
      transform: translateX(-50%);
      background: #1c1c1e; border: 1px solid rgba(255,255,255,0.12);
      border-radius: 14px; padding: 8px;
      min-width: 230px; max-width: 300px; max-height: 340px;
      overflow: hidden; flex-direction: column; gap: 4px;
      box-shadow: 0 12px 40px rgba(0,0,0,0.6);
      z-index: 200; display: none;
    }}
    .custom-select.open .cs-panel {{ display: flex; }}
    .cs-search {{
      width: 100%; flex-shrink: 0;
      background: rgba(255,255,255,0.07);
      border: 1px solid rgba(255,255,255,0.10);
      border-radius: 8px; padding: 6px 10px;
      font-size: 13px; color: #fff; outline: none;
    }}
    .cs-search::placeholder {{ color: rgba(255,255,255,0.3); }}
    .cs-list {{ overflow-y: auto; flex: 1; }}
    .cs-item {{
      display: flex; align-items: center; gap: 8px;
      padding: 7px 8px; border-radius: 8px;
      cursor: pointer; transition: background 0.1s;
    }}
    .cs-item:hover {{ background: rgba(255,255,255,0.07); }}
    .cs-item.selected {{ background: rgba(0,113,227,0.12); }}
    .cs-logo {{ width: 18px; height: 18px; object-fit: contain; flex-shrink: 0; border-radius: 3px; background: #fff; padding: 2px; box-sizing: border-box; }}

    /* ── Company grid dropdown ── */
    #cs-company .cs-panel {{ min-width: 420px; max-width: 520px; max-height: 400px; }}
    .cs-grid {{ display: flex; flex-wrap: wrap; gap: 5px; padding: 4px 2px; overflow-y: auto; }}
    .cs-grid-item {{
      display: flex; flex-direction: column; align-items: center; gap: 5px;
      padding: 8px 5px 6px; border-radius: 8px; cursor: pointer;
      width: 76px; transition: background 0.1s; flex-shrink: 0;
    }}
    .cs-grid-item:hover {{ background: rgba(255,255,255,0.07); }}
    .cs-grid-item.selected {{ background: rgba(0,113,227,0.15); outline: 1.5px solid var(--blue); }}
    .cs-grid-logo {{ width: 36px; height: 36px; object-fit: contain; border-radius: 6px; background: #fff; padding: 3px; box-sizing: border-box; }}
    .cs-grid-lbl {{ font-size: 10px; color: rgba(255,255,255,0.65); text-align: center; line-height: 1.2; width: 66px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    .cs-grid-item.selected .cs-grid-lbl {{ color: #fff; }}
    .cs-lbl {{ font-size: 13px; color: rgba(255,255,255,0.82); flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    .cs-check {{
      width: 16px; height: 16px; border-radius: 4px;
      border: 1.5px solid rgba(255,255,255,0.2);
      display: flex; align-items: center; justify-content: center;
      flex-shrink: 0; transition: all 0.1s;
    }}
    .cs-item.selected .cs-check {{ background: var(--blue); border-color: var(--blue); }}
    .cs-tick {{ display: none; width: 9px; height: 8px; }}
    .cs-item.selected .cs-tick {{ display: block; }}
    .cs-empty {{ font-size: 13px; color: rgba(255,255,255,0.3); padding: 12px 8px; text-align: center; }}

    /* ── Radius filter ── */
    .radius-select {{
      font-size: 12.5px; padding: 5px 28px 5px 11px;
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.10);
      border-radius: 980px; color: rgba(255,255,255,0.55);
      cursor: pointer; outline: none; appearance: none; font-weight: 500;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M1 1l4 4 4-4' stroke='rgba(255,255,255,0.4)' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
      background-repeat: no-repeat; background-position: right 9px center;
      transition: all 0.15s;
    }}
    .radius-select option {{ background: #111113; }}
    .radius-select:hover {{ color: #fff; border-color: rgba(255,255,255,0.2); background-color: rgba(255,255,255,0.10); }}
    .radius-select.active {{ border-color: var(--blue); color: #fff; background-color: rgba(0,113,227,0.18); }}

    /* ── Count bar ── */
    .count-bar {{
      max-width: 1400px; margin: 28px auto 0; padding: 0 28px;
      font-size: 13px; color: var(--muted);
    }}

    /* ── Job list (one row per job) ── */
    .grid {{
      max-width: 1400px; margin: 16px auto 80px; padding: 0 28px;
      display: flex; flex-direction: column;
    }}
    .job-head, .card {{
      display: grid; align-items: center; column-gap: 14px;
      grid-template-columns: 22px 130px minmax(0,1fr) 240px 64px 78px 44px;
      grid-template-areas: "logo company title city date actions score";
      padding: 10px 14px;
    }}
    .job-head {{
      font-size: 11px; font-weight: 600; color: var(--muted);
      text-transform: uppercase; letter-spacing: 0.4px; padding-bottom: 6px;
    }}
    .job-head .h-score {{ text-align: right; }}
    .card {{
      background: var(--white); border-bottom: 1px solid #ececf0;
      transition: background 0.15s;
    }}
    .grid > .card:first-of-type {{ border-radius: 12px 12px 0 0; }}
    .grid > .card:last-of-type  {{ border-radius: 0 0 12px 12px; border-bottom: none; }}
    .card:hover {{ background: #f7f8fa; }}

    .logo {{ grid-area: logo; width: 22px; height: 22px; object-fit: contain; }}
    .company-label {{
      grid-area: company; font-size: 13px; color: var(--muted); font-weight: 500;
      overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    }}
    .card-title {{ grid-area: title; min-width: 0; font-size: 14px; font-weight: 600; line-height: 1.35; }}
    .card-title a {{ color: inherit; text-decoration: none; }}
    .card-title a:hover {{ color: var(--blue); }}
    .card-sub {{
      font-size: 11.5px; font-weight: 400; color: #8e8e93; margin-top: 2px;
      overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    }}
    .card-city {{
      grid-area: city; font-size: 12.5px; color: #3a3a3c; line-height: 1.35;
      overflow: hidden; display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2;
    }}
    .card-date {{ grid-area: date; font-size: 12px; color: #8e8e93; line-height: 1.3; }}
    .card-date span {{ cursor: default; border-bottom: 1px dashed #c7c7cc; }}
    .card-date .first-seen {{ font-style: italic; }}
    .card-date .gone {{ display: block; font-size: 10.5px; border-bottom: none; }}
    .card-actions {{ grid-area: actions; display: flex; justify-content: flex-end; gap: 2px; }}
    .card-score {{ grid-area: score; text-align: right; }}
    .new-badge {{
      font-size: 9.5px; font-weight: 700; vertical-align: 2px; margin-right: 6px;
      background: #34c759; color: #fff;
      border-radius: 5px; padding: 1px 6px; letter-spacing: 0.4px;
    }}
    .match-badge {{
      font-size: 10px; font-weight: 700; color: #fff;
      border-radius: 5px; padding: 2px 7px; letter-spacing: 0.3px;
      cursor: help;
    }}
    .card-hide-btn {{
      background: none; border: none; cursor: pointer; padding: 2px 4px;
      font-size: 12px; color: rgba(0,0,0,0.2); line-height: 1;
      transition: color 0.15s;
    }}
    .card-hide-btn:hover {{ color: #ff3b30; }}

    @media (max-width: 720px) {{
      .grid {{ padding: 0 16px; }}
      .job-head {{ display: none; }}
      .card {{
        grid-template-columns: 22px minmax(0,1fr) auto auto;
        grid-template-areas:
          "logo company date  score"
          "title title  title title"
          "city  city   actions actions";
        row-gap: 4px;
      }}
      .card-date {{ text-align: right; }}
      .card-date .gone {{ display: inline; margin-left: 4px; }}
    }}

    .no-results {{
      grid-column: 1/-1; text-align: center;
      padding: 80px 0; font-size: 19px; color: var(--muted);
    }}

    /* ── Pagination ── */
    .pagination {{
      display: flex; align-items: center; justify-content: center;
      gap: 8px; padding: 24px 28px 64px;
    }}
    .page-btn {{
      height: 36px; min-width: 36px; padding: 0 14px;
      background: var(--white); border: 1px solid #d2d2d7;
      border-radius: 10px; font-size: 14px; font-weight: 500;
      color: var(--near-black); cursor: pointer;
      transition: background 0.15s, border-color 0.15s;
    }}
    .page-btn:hover:not(:disabled) {{ background: #f5f5f7; border-color: #b0b0b5; }}
    .page-btn:disabled {{ opacity: 0.35; cursor: default; }}
    .page-btn.active {{ background: var(--blue); border-color: var(--blue); color: #fff; }}
    .page-label {{ font-size: 13px; color: var(--muted); padding: 0 6px; }}

    .card-star-btn {{
      background: none; border: none; cursor: pointer; padding: 2px 4px;
      font-size: 17px; color: rgba(0,0,0,0.2); line-height: 1;
      transition: color 0.15s, transform 0.15s; flex-shrink: 0;
    }}
    .card-star-btn:hover {{ color: #ff9f0a; transform: scale(1.2); }}
    .card-star-btn.saved {{ color: #ff9f0a; }}
    .card-apply-btn {{
      background: none; border: none; cursor: pointer; padding: 2px 4px;
      font-size: 15px; color: rgba(0,0,0,0.2); line-height: 1;
      transition: color 0.15s, transform 0.15s; flex-shrink: 0;
    }}
    .card-apply-btn:hover {{ color: var(--blue); transform: scale(1.2); }}
    .card-apply-btn.applied {{ color: #34c759; }}
    .pill-fav {{ position: relative; }}
    .pill-fav-count {{
      position: absolute; top: -6px; right: -6px;
      background: #ff9f0a; color: #fff; border-radius: 8px;
      font-size: 10px; font-weight: 700; padding: 1px 5px; min-width: 16px; text-align: center;
    }}
    .cs-grid-item {{ position: relative; }}
    .fav-star {{
      position: absolute; top: 4px; right: 4px;
      background: none; border: none; cursor: pointer; padding: 0;
      font-size: 13px; line-height: 1; color: rgba(255,255,255,0.15);
      transition: color 0.15s, transform 0.15s; z-index: 1;
    }}
    .cs-grid-item:hover .fav-star {{ color: rgba(255,255,255,0.55); }}
    .fav-star:hover {{ color: #ff9f0a !important; transform: scale(1.2); }}
    .fav-star.active {{ color: #ff9f0a; }}
    .cs-grid-item:hover .fav-star.active {{ color: #ff9f0a; }}
    .cs-item .fav-star {{ position: static; font-size: 14px; margin-left: 4px; flex-shrink: 0; }}
    .pill-fav-cities {{ position: relative; }}
    .pill-fav-cities-count {{
      position: absolute; top: -6px; right: -6px;
      background: #5ac8fa; color: #fff; border-radius: 8px;
      font-size: 10px; font-weight: 700; padding: 1px 5px; min-width: 16px; text-align: center;
    }}

    /* ── Stats overlay ── */
    .stats-overlay {{
      display: none; position: fixed; inset: 0; z-index: 1000;
      background: rgba(0,0,0,0.55); backdrop-filter: blur(4px);
      align-items: center; justify-content: center;
    }}
    .stats-overlay.open {{ display: flex; }}
    .stats-modal {{
      background: #f5f5f7; color: #1d1d1f;
      border-radius: 16px; width: min(880px,96vw); max-height: 82vh;
      display: flex; flex-direction: column; overflow: hidden;
      box-shadow: 0 24px 60px rgba(0,0,0,0.4);
    }}
    .stats-header {{
      display: flex; align-items: center; justify-content: space-between;
      padding: 16px 20px; border-bottom: 1px solid #d1d1d6;
      font-weight: 600; font-size: 16px; color: #1d1d1f;
    }}
    .stats-header-right {{ display: flex; align-items: center; gap: 12px; }}
    .stats-search {{
      background: #fff; border: 1px solid #c7c7cc;
      border-radius: 8px; color: #1d1d1f; padding: 6px 12px; font-size: 13px; width: 200px;
    }}
    .stats-search:focus {{ outline: none; border-color: var(--blue); }}
    .stats-close {{
      background: none; border: none; color: #6e6e73; font-size: 18px;
      cursor: pointer; padding: 4px 8px; border-radius: 6px;
    }}
    .stats-close:hover {{ color: #1d1d1f; background: rgba(0,0,0,0.07); }}
    .stats-table-wrap {{ overflow-y: auto; flex: 1; }}
    .stats-table {{
      width: 100%; border-collapse: collapse; font-size: 13px;
    }}
    .stats-table thead th {{
      position: sticky; top: 0; background: #f5f5f7;
      padding: 10px 14px; text-align: left; color: #6e6e73;
      font-weight: 600; border-bottom: 1px solid #d1d1d6;
      cursor: pointer; white-space: nowrap; user-select: none;
    }}
    .stats-table thead th:hover {{ color: #1d1d1f; }}
    .stats-table thead th.sort-asc::after  {{ content: ' ▲'; color: var(--blue); }}
    .stats-table thead th.sort-desc::after {{ content: ' ▼'; color: var(--blue); }}
    .stats-table tbody tr {{ border-bottom: 1px solid #e5e5ea; cursor: pointer; }}
    .stats-table tbody tr:hover {{ background: #ebebf0; }}
    .stats-table td {{ padding: 9px 14px; vertical-align: middle; color: #1d1d1f; }}
    .stats-company-cell {{ display: flex; align-items: center; gap: 10px; font-weight: 500; color: #1d1d1f; }}
    .stats-logo {{ width: 22px; height: 22px; object-fit: contain; border-radius: 4px; }}
    .stats-total {{ font-weight: 600; color: #1d1d1f; }}
    .stats-new {{ color: #1a7f37; font-weight: 600; }}
    .stats-new.zero {{ color: #aeaeb2; font-weight: 400; }}
    .stats-posted {{ color: #0071e3; font-weight: 600; }}
    .stats-posted.zero {{ color: #aeaeb2; font-weight: 400; }}
    .stats-status {{ font-size: 14px; text-align: center; }}
    .stats-footer {{
      padding: 10px 20px; border-top: 1px solid #d1d1d6;
      font-size: 12px; color: #6e6e73; text-align: right;
    }}
  </style>
</head>
<body>

<div class="hero">
  <p>{len(active_jobs):,} open jobs{' · ' + format(len(archived_jobs), ',') + ' archived' if archived_jobs else ''}{' · ' + str(new_count) + ' new today' if new_count else ''}{' · Updated ' + scraped_at if scraped_at else ''}</p>
</div>

<div class="controls-bar">
  <div class="search-wrap">
    <svg class="s-icon" viewBox="0 0 20 20"><circle cx="8.5" cy="8.5" r="5.5"/><line x1="13" y1="13" x2="18" y2="18"/></svg>
    <input class="search-input" id="q" type="search" placeholder="Search jobs…" autocomplete="off"/>
  </div>
  <div class="filter-strip">
    <button class="pill active" data-new="all">All</button>
    <button class="pill" data-new="new">✦ New</button>
    <button class="pill pill-fav" id="pill-fav">⭐ My Companies<span class="pill-fav-count" id="fav-count" style="display:none">0</span></button>
    <button class="pill pill-fav-cities" id="pill-fav-cities">🏙 My Cities<span class="pill-fav-cities-count" id="fav-cities-count" style="display:none">0</span></button>
    <div class="fsep"></div>
    <button class="pill active" data-region="us">🇺🇸 US</button>
    <button class="pill" data-region="all">🌐 All</button>
    <div class="fsep"></div>
    <div class="custom-select" id="cs-company">
      <button class="cs-btn"><span class="cs-btn-label">Company</span><span class="cs-badge"></span><svg class="cs-chevron" width="10" height="6" viewBox="0 0 10 6" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M1 1l4 4 4-4"/></svg></button>
      <div class="cs-panel"><input class="cs-search" placeholder="Search…" autocomplete="off"/><div class="cs-list"></div></div>
    </div>
    <div class="custom-select" id="cs-team">
      <button class="cs-btn"><span class="cs-btn-label">Team</span><span class="cs-badge"></span><svg class="cs-chevron" width="10" height="6" viewBox="0 0 10 6" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M1 1l4 4 4-4"/></svg></button>
      <div class="cs-panel"><input class="cs-search" placeholder="Search…" autocomplete="off"/><div class="cs-list"></div></div>
    </div>
    <div class="custom-select" id="cs-city">
      <button class="cs-btn"><span class="cs-btn-label">City</span><span class="cs-badge"></span><svg class="cs-chevron" width="10" height="6" viewBox="0 0 10 6" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M1 1l4 4 4-4"/></svg></button>
      <div class="cs-panel"><input class="cs-search" placeholder="Search cities…" autocomplete="off"/><div class="cs-list"></div></div>
    </div>
    <select class="radius-select" id="radius-miles">
      <option value="">Any dist</option>
      <option value="25">25 mi</option>
      <option value="50">50 mi</option>
      <option value="100">100 mi</option>
      <option value="200">200 mi</option>
    </select>
    <div class="custom-select" id="cs-exp">
      <button class="cs-btn"><span class="cs-btn-label">Level</span><span class="cs-badge"></span><svg class="cs-chevron" width="10" height="6" viewBox="0 0 10 6" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M1 1l4 4 4-4"/></svg></button>
      <div class="cs-panel"><div class="cs-list"></div></div>
    </div>
    <div class="fsep"></div>
    <button class="pill" data-sort="newest">Newest</button>
    <button class="pill active" data-sort="foryou">✦ For You</button>
    <button class="pill" data-sort="saved">★ Saved</button>
    <button class="pill" data-sort="applied">➔ Applied</button>
    <button class="pill" data-sort="archive" title="Jobs no longer listed on the company's site">🗄 Archive</button>
    <select class="radius-select" id="archive-month" style="display:none"></select>
    <div class="fsep"></div>
    <button class="pill" id="export-btn">⬇ CSV</button>
    <button class="pill" id="stats-btn">📊 Stats</button>
  </div>
</div>

<div class="count-bar"><span id="count-label"></span><span id="current-day-label" style="margin-left:8px;color:#8e8e93"></span><button id="next-day-btn" class="page-btn" style="display:none;margin-left:10px;height:26px;min-width:auto;padding:0 10px;font-size:12px;vertical-align:middle">Next Day ⇥</button><span id="hidden-label" style="margin-left:10px;font-size:12px;color:#8e8e93"></span></div>
<div class="grid" id="grid"></div>
<div class="pagination" id="pagination"></div>

<!-- Stats modal -->
<div class="stats-overlay" id="stats-overlay">
  <div class="stats-modal">
    <div class="stats-header">
      <span>📊 Company Stats</span>
      <div class="stats-header-right">
        <input class="stats-search" id="stats-search" placeholder="Search companies…" autocomplete="off"/>
        <button class="stats-close" id="stats-close">✕</button>
      </div>
    </div>
    <div class="stats-table-wrap">
      <table class="stats-table">
        <thead>
          <tr>
            <th data-col="company">Company</th>
            <th data-col="total" class="sort-desc">Total Jobs</th>
            <th data-col="new">New Today</th>
            <th data-col="posted">Posted 24h</th>
            <th data-col="status">Health</th>
          </tr>
        </thead>
        <tbody id="stats-tbody"></tbody>
      </table>
    </div>
    <div class="stats-footer" id="stats-footer"></div>
  </div>
</div>

<script type="application/json" id="jobs-data">{jobs_json_embed}</script>
<script>
function decodeJobs(c) {{
  const cols = Object.keys(c).filter(k => k !== 'n');
  const out = new Array(c.n);
  for (let i = 0; i < c.n; i++) {{
    const j = {{}};
    for (const k of cols) {{
      const v = c[k];
      j[k] = Array.isArray(v) ? v[i] : v.d[v.i[i]];
    }}
    j.is_new = !!j.is_new;
    out[i] = j;
  }}
  return out;
}}
const JOBS        = decodeJobs(JSON.parse(document.getElementById('jobs-data').textContent));
const JOB_IDS     = new Set(JOBS.map(j => j.role_id));

// Archived jobs live in archive/<YYYY-MM>.json (by first-seen month), loaded on demand.
const ARCHIVE_MONTHS = {archive_months_json};
const _archiveCache  = new Map();  // month -> Promise<jobs[]>
let   ARCHIVE        = [];         // jobs for the month picked in the Archive tab
function loadArchiveMonth(month) {{
  if (!_archiveCache.has(month)) {{
    _archiveCache.set(month, fetch(`archive/${{month}}.json`)
      .then(r => {{ if (!r.ok) throw new Error(r.status); return r.json(); }})
      .then(decodeJobs)
      .catch(err => {{ _archiveCache.delete(month); throw err; }}));
  }}
  return _archiveCache.get(month);
}}
// Every archive month fetched so far, flattened; used so Saved/Applied still show
// jobs that dropped off their company's site after being saved.
let _loadedArchived = [];
async function loadAllArchive() {{
  const lists = await Promise.all(ARCHIVE_MONTHS.map(m => loadArchiveMonth(m.month)));
  _loadedArchived = lists.flat();
}}
const LOGOS       = {logos_json};
const TEAMS       = {teams_json};
const COMPANIES   = {companies_json};
const EXPERIENCES = {experiences_json};
const SA          = {state_abbrev_json};
const US_ST       = new Set(Object.values(SA));
const CITY_COORDS = {city_coords_json};

function haversine(lat1, lon1, lat2, lon2) {{
  const R = 3958.8;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat/2)**2 + Math.cos(lat1*Math.PI/180)*Math.cos(lat2*Math.PI/180)*Math.sin(dLon/2)**2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
}}

// Cities that share a 2-letter code with a US state but are NOT in the US
const INTL_CITY_HINT = new Set([
  'bangalore','bengaluru','hyderabad','mumbai','delhi','new delhi','pune','chennai',
  'kolkata','noida','gurgaon','gurugram','ahmedabad','kochi','jaipur','indore','nagpur',
  'toronto','vancouver','montreal','ottawa','calgary','edmonton','winnipeg','halifax',
  'london','manchester','edinburgh','bristol','leeds','birmingham','glasgow','dublin',
  'amsterdam','berlin','munich','frankfurt','hamburg','cologne','stuttgart','paris',
  'lyon','marseille','madrid','barcelona','seville','milan','rome','turin','naples',
  'sydney','melbourne','brisbane','perth','adelaide','auckland','wellington','christchurch',
  'singapore','tokyo','osaka','kyoto','sapporo','beijing','shanghai','shenzhen',
  'guangzhou','hong kong','seoul','busan','taipei','kaohsiung','bangkok','jakarta',
  'kuala lumpur','manila','ho chi minh','hanoi','tel aviv','jerusalem','dubai',
  'abu dhabi','riyadh','doha','cairo','nairobi','lagos','johannesburg','cape town',
  'mexico city','guadalajara','monterrey','bogota','lima','santiago','sao paulo',
  'rio de janeiro','buenos aires','stockholm','oslo','copenhagen','helsinki',
  'zurich','geneva','bern','brussels','antwerp','vienna','warsaw','prague',
  'budapest','bucharest','athens','lisbon','porto'
]);

function normalizeLocation(loc) {{
  if (!loc) return null;
  // Strip zip codes
  let s = loc.replace(/\b\d{{5}}(-\d{{4}})?\b/g, '').replace(/\s+/g, ' ').trim();
  const parts = s.split(/\s*,\s*/).map(p => p.trim()).filter(Boolean);
  if (!parts.length) return null;
  const city = parts[0];
  const cityLc = city.toLowerCase();

  for (let i = 1; i < parts.length; i++) {{
    const p = parts[i];
    if (US_ST.has(p) && !INTL_CITY_HINT.has(cityLc))  return {{ display: `${{city}}, ${{p}}`,    isUS: true }};
    if (SA[p]        && !INTL_CITY_HINT.has(cityLc))   return {{ display: `${{city}}, ${{SA[p]}}`, isUS: true }};
    if (/^(USA|United States|US)$/i.test(p)) {{
      for (let k = i - 1; k >= 1; k--) {{
        if (US_ST.has(parts[k])) return {{ display: `${{city}}, ${{parts[k]}}`,    isUS: true }};
        if (SA[parts[k]])        return {{ display: `${{city}}, ${{SA[parts[k]]}}`, isUS: true }};
      }}
      return {{ display: city, isUS: true }};
    }}
  }}

  // "Pittsburgh PA" style — no comma, state abbrev at end
  const m = city.match(/^(.+?)\s+([A-Z]{{2}})$/);
  if (m && US_ST.has(m[2]) && !INTL_CITY_HINT.has(m[1].toLowerCase())) return {{ display: `${{m[1]}}, ${{m[2]}}`, isUS: true }};

  // International: "City, Country"
  if (parts.length >= 2) return {{ display: `${{city}}, ${{parts[parts.length - 1]}}`, isUS: false }};
  return {{ display: city, isUS: false }};
}}

// Parse all locations from a job (handles newline-delimited multi-location strings)
function getLocations(j) {{
  const raw = (j.location || '').trim();
  if (!raw) return [];
  const parts = raw.split(/\\r?\\n/).map(s => s.trim()).filter(Boolean);
  const results = [];
  parts.forEach(p => {{
    // "PA - Pittsburgh (15222)" or "PA - Pittsburgh" format
    const m = p.match(/^([A-Z]{{2}})\s*[-–]\s*(.+?)(?:\s*\(\d+\))?$/);
    if (m && US_ST.has(m[1]) && !INTL_CITY_HINT.has(m[2].trim().toLowerCase())) {{
      results.push({{ display: `${{m[2].trim()}}, ${{m[1]}}`, isUS: true }});
      return;
    }}
    const n = normalizeLocation(p);
    if (n) results.push(n);
  }});
  return results;
}}


// ── For You scoring ──
function scoreJobDetailed(j) {{
  const title = (j.title || '').toLowerCase();
  const team  = (j.team  || '').toLowerCase();
  const exp   = (j.experience || '').toLowerCase();
  const breakdown = [];

  // Hard blocks — physical/non-tech roles score 0 regardless of team
  if (/\\b(security[\\s-]*officer|police[\\s-]*officer|security[\\s-]*guard|armed[\\s-]*guard|unarmed[\\s-]*guard|warehouse[\\s-]*(worker|associate|operative|clerk|technician)|forklift|truck[\\s-]*driver|custodian|janitorial|janitor|correctional|food[\\s-]*service[\\s-]*(worker|associate)|assembl(er|y[\\s-]*worker|y[\\s-]*tech))\\b/.test(title)) {{
    return {{ score: 0, breakdown: [{{ label: 'Non-tech / physical role', delta: 0 }}] }};
  }}

  let s = 10;
  breakdown.push({{ label: 'Base score', delta: 10 }});
  const add = (delta, label) => {{ s += delta; breakdown.push({{ label, delta }}); }};

  // Intern / co-op boost
  if (/\\b(intern|internship|co-?op)\\b/.test(title)) add(50, 'Intern / co-op title');

  // Research boost
  if (/\\b(research\\s*(scientist|engineer)|applied\\s*research)\\b/.test(title)) add(20, 'Research role');

  // Computer vision / NLP boost
  if (/\\b(computer\\s*vision|\\bnlp\\b|natural\\s*language\\s*processing)\\b/.test(title)) add(20, 'Computer vision / NLP');

  // Data roles
  if (/data[\\s-]?(engineer|analyst|scientist|science|pipelin)/.test(title)) add(40, 'Data engineer/analyst/scientist title');
  else if (/\\b(data|analytics|sql|\\bbi\\b|business[\\s-]*intelligence|etl|data[\\s-]*warehouse)\\b/.test(title)) add(22, 'Data-adjacent title');

  // Software / SWE
  if (/\\b(software[\\s-]*(engineer|developer)|software\\s+\\w+\\s+(engineer|developer)|swe|sde|developer|programmer)\\b/.test(title)) add(40, 'Software engineer/developer title');

  // ML / AI
  if (/\\b(machine[\\s-]*learning|\\bml\\b|\\bai\\b|artificial[\\s]*intel|deep[\\s]*learning|\\bllm\\b|gen[\\s-]*ai)\\b/.test(title)) add(35, 'ML / AI title');

  // Frontend / Backend / Fullstack / Web / Mobile
  if (/\\b(backend|frontend|full[\\s-]?stack|web[\\s-]*(dev(eloper)?|engineer)|mobile[\\s-]*(dev(eloper)?|engineer))\\b/.test(title)) add(22, 'Frontend/backend/fullstack/mobile');

  // IT / DevOps / Cloud / Infra / Systems / Network / Database / Help Desk
  if (/\\b(information[\\s-]*tech|\\bit\\b|devops|cloud|platform|\\bsre\\b|infrastructure|systems?[\\s-]*(admin(istrator)?|engineer|analyst)|network[\\s-]*(engineer|admin(istrator)?|architect|analyst|specialist|tech)|database[\\s-]*(admin(istrator)?|engineer|developer|analyst|architect)|help[\\s-]*desk|it[\\s-]*support|technical[\\s-]*support|service[\\s-]*desk|site[\\s-]*reliability)\\b/.test(title)) add(28, 'IT/DevOps/Cloud/Infra/Systems/Network/DB');

  // ServiceNow developer/admin — doesn't match the generic "software developer" pattern above
  if (/\\bservicenow\\b/.test(title) || /\\bservicenow\\b/.test(team)) add(30, 'ServiceNow role');

  // Cybersecurity (security engineer/analyst — NOT officer/guard, blocked above)
  if (/\\b(cyber(security)?|security[\\s-]*(engineer|analyst|architect|specialist|consultant)|application[\\s-]*security|pen[\\s-]*test(er|ing)?|penetration[\\s-]*test|soc[\\s-]*analyst|incident[\\s-]*response|threat[\\s-]*(intel|analyst)|vulnerability[\\s-]*(analyst|engineer)|information[\\s-]*security)\\b/.test(title)) add(28, 'Cybersecurity role');

  // QA / Testing
  if (/\\b(\\bqa\\b|\\bqe\\b|quality[\\s-]*(assurance|engineer|analyst)|test[\\s-]*(engineer|analyst|developer|automation)|\\bsdet\\b|automation[\\s-]*test(er|ing)?)\\b/.test(title)) add(22, 'QA / Testing role');

  // Entry-level signals — generic
  if (/\\b(junior|entry[\\s-]?level|new[\\s-]*grad|early[\\s-]*career|level\\s*i\\b)\\b/.test(title)) add(28, 'Entry-level signal in title');
  // "associate" only boosts when paired with a tech role word
  if (/\\bassociate\\b/.test(title) && /\\b(software|engineer|developer|analyst|data|scientist|swe|sde|programmer|devops|cloud|it|security|architect|network|database|qa|systems?)\\b/.test(title)) add(28, '"Associate" + tech role');
  if (/\\b(junior|entry[\\s-]?level|new[\\s-]*grad|associate)\\b/.test(exp)) add(35, 'Entry-level signal in experience field');

  // ── Company-specific level systems ──
  // Google: L3=SWE II (entry), L4=SWE III (junior-mid), L5+=Senior (penalised below)
  if (/\\b(swe\\s*(ii|2)|sde\\s*(ii|2)|software\\s*engineer\\s*(ii|2)|data\\s*engineer\\s*(ii|2))\\b/.test(title)) add(30, 'Level II (Google-style)');
  if (/\\b(swe\\s*(iii|3)|sde\\s*(iii|3)|software\\s*engineer\\s*(iii|3))\\b/.test(title)) add(12, 'Level III (Google-style)');
  if (/\\b(swe\\s*(iv|v|4|5|6)|software\\s*engineer\\s*(iv|v|4|5|6))\\b/.test(title)) add(-30, 'Level IV+ (Google-style, senior)');
  // Meta: E3/E4 entry-junior, E5+ senior
  if (/\\bE[34]\\b/.test(title)) add(28, 'E3/E4 (Meta-style, entry-junior)');
  if (/\\bE[56789]\\b/.test(title)) add(-35, 'E5+ (Meta-style, senior)');
  // Amazon: SDE I=entry (L4), SDE II=mid (L5), Senior SDE=senior (L6)
  // "sde" already +40; SDE I specifically gets extra boost
  if (/\\bsde\\s*i\\b/.test(title) && !/\\bsde\\s*ii\\b/.test(title)) add(20, 'SDE I (Amazon-style, entry)');
  // Microsoft: SDE=entry, SDE II=mid, Senior SDE=senior — handled by "sde" +40 + senior penalty
  // Apple: ICT2/ICT3 entry, ICT4 mid, ICT5/6 senior
  if (/\\bict\\s*[23]\\b/.test(title)) add(28, 'ICT2/3 (Apple-style, entry)');
  if (/\\bict\\s*4\\b/.test(title)) add(5, 'ICT4 (Apple-style, mid)');
  if (/\\bict\\s*[567]\\b/.test(title)) add(-30, 'ICT5+ (Apple-style, senior)');
  // Stripe: IC3=entry, IC4=junior-mid, IC5+=senior
  if (/\\bic\\s*[34]\\b/.test(title)) add(25, 'IC3/4 (Stripe-style, entry-mid)');
  if (/\\bic\\s*[567]\\b/.test(title)) add(-30, 'IC5+ (Stripe-style, senior)');
  // Uber/Airbnb/Snap/Pinterest/Roblox: L3/L4=entry-mid, L5+=senior
  if (/\\b(software|swe|sde|data|ml)\\b/.test(title) && /\\bl[34]\\b/.test(title)) add(22, 'L3/L4 (Uber/Airbnb-style, entry-mid)');
  if (/\\b(software|swe|sde|data|ml)\\b/.test(title) && /\\bl[5678]\\b/.test(title)) add(-30, 'L5+ (Uber/Airbnb-style, senior)');
  // Salesforce: MTS=entry, SMTS=senior, LMTS/PMTS=staff
  if (/\\bmts\\b/.test(title) && !/\\b(s|l|p)mts\\b/.test(title)) add(20, 'MTS (Salesforce-style, entry)');
  if (/\\b(smts|lmts|pmts)\\b/.test(title)) add(-25, 'SMTS/LMTS/PMTS (Salesforce-style, senior/staff)');
  // EA: Associate SE / SE I = entry
  if (/\\bse\\s*i\\b/.test(title) && !/\\bse\\s*ii\\b/.test(title)) add(20, 'SE I (EA-style, entry)');
  // Ubisoft: Junior Programmer handled by "junior"; Programmer=mid; Senior=penalised below
  // PNC: C1 Associate=caught by "associate"; C2 SWE neutral; C3+ Senior/Principal caught below

  // Seniority penalties
  if (/\\b(senior|sr\\.?\\s|staff\\s|principal)/.test(title)) add(-35, 'Senior/staff/principal in title');
  if (/\\b(director|vp\\b|vice\\s*president|head\\s+of|chief|\\bpresident\\b)/.test(title)) add(-50, 'Director/VP/Chief in title');
  if (/\\bmanager\\b/.test(title)) add(-20, '"Manager" in title');
  if (/\\b(senior|staff|principal)/.test(exp)) add(-30, 'Senior/staff/principal in experience field');

  // Team boost
  if (/\\b(engineering|software|data|analytics|\\bml\\b|\\bai\\b|\\bit\\b|technology|infrastructure|platform|cloud|security|cyber|network|database|\\bqa\\b|devops|systems?)\\b/.test(team)) add(15, 'Tech team');

  // Non-tech role penalties (when not paired with tech words)
  const hasTech = /\\b(software|engineer|developer|data|analyst|science|\\bit\\b|tech|digital|analytics|automation|platform|cloud|devops|security|network|database|\\bqa\\b|systems?|\\bsre\\b|\\bswe\\b|\\bsde\\b|programmer|architect|\\bml\\b|\\bai\\b)\\b/.test(title);
  if (!hasTech) {{
    if (/\\b(sales\\s+(executive|director|manager|lead)|account\\s+(executive|manager))\\b/.test(title)) add(-30, 'Non-tech: sales role');
    if (/\\b(legal|attorney|counsel|paralegal|compliance\\s+officer)\\b/.test(title)) add(-25, 'Non-tech: legal role');
    if (/\\b(human\\s+resources?|\\bhr\\s+(manager|coordinator|specialist|generalist|business\\s+partner)|\\bhrbp\\b)\\b/.test(title)) add(-25, 'Non-tech: HR role');
    if (/\\b(marketing\\s+(manager|director|specialist|coordinator|strategist)|brand\\s+manager|growth\\s+marketer|content\\s+(marketer|writer|strategist)|\\bseo\\b|social\\s+media)\\b/.test(title)) add(-20, 'Non-tech: marketing role');
    if (/\\b(finance\\s+(manager|analyst|director)|financial\\s+(analyst|advisor|planner|controller)|\\baccounting\\b|accountant|\\bcpa\\b|\\bcontroller\\b|bookkeeper|payroll\\s+(specialist|coordinator))\\b/.test(title)) add(-20, 'Non-tech: finance role');
  }}

  const pBonus = personalizedBonus(j);
  if (pBonus) breakdown.push({{ label: 'Learned from your Applied jobs', delta: pBonus }});
  s += pBonus;

  const score = Math.max(0, Math.min(100, s));
  return {{ score, breakdown }};
}}
const _scoreCache = new Map();
function scoreJob(j) {{
  let s = _scoreCache.get(j.role_id);
  if (s === undefined) {{ s = scoreJobDetailed(j).score; _scoreCache.set(j.role_id, s); }}
  return s;
}}

// ── Custom multi-select dropdown factory ──
function makeDropdown(containerId, getItems, iconFn, gridMode, favOpts) {{
  const wrap     = document.getElementById(containerId);
  const btn      = wrap.querySelector('.cs-btn');
  const badge    = wrap.querySelector('.cs-badge');
  const panel    = wrap.querySelector('.cs-panel');
  const searchEl = wrap.querySelector('.cs-search');
  const list     = wrap.querySelector('.cs-list');
  const sel      = new Set();
  let q = '';

  function renderItems() {{
    list.innerHTML = '';
    const items = getItems().filter(v => !q || v.toLowerCase().includes(q.toLowerCase()));
    if (!items.length) {{ list.innerHTML = '<div class="cs-empty">No results</div>'; return; }}
    const frag = document.createDocumentFragment();
    if (gridMode) {{
      const grid = document.createElement('div');
      grid.className = 'cs-grid';
      items.forEach(v => {{
        const icon = iconFn ? iconFn(v) : null;
        const d = document.createElement('div');
        d.className = 'cs-grid-item' + (sel.has(v) ? ' selected' : '');
        if (icon) {{ const img=document.createElement('img'); img.className='cs-grid-logo'; img.src=icon; img.alt=''; d.appendChild(img); }}
        const lbl=document.createElement('span'); lbl.className='cs-grid-lbl'; lbl.textContent=v; lbl.title=v; d.appendChild(lbl);
        const star = document.createElement('button');
        star.className = 'fav-star' + (isFav(v) ? ' active' : '');
        star.textContent = isFav(v) ? '★' : '☆';
        star.title = isFav(v) ? 'Remove from My Companies' : 'Add to My Companies';
        star.addEventListener('mousedown', e => {{
          e.preventDefault(); e.stopPropagation();
          toggleFav(v);
          star.textContent = isFav(v) ? '★' : '☆';
          star.classList.toggle('active', isFav(v));
          star.title = isFav(v) ? 'Remove from My Companies' : 'Add to My Companies';
          if (state.favOnly) render();
        }});
        d.appendChild(star);
        d.addEventListener('mousedown', e => {{
          e.preventDefault();
          sel.has(v) ? sel.delete(v) : sel.add(v);
          d.classList.toggle('selected', sel.has(v));
          badge.textContent = sel.size || '';
          badge.style.display = sel.size ? '' : 'none';
          btn.classList.toggle('active', sel.size > 0);
          render();
        }});
        grid.appendChild(d);
      }});
      frag.appendChild(grid);
    }} else {{
      items.forEach(v => {{
        const icon = iconFn ? iconFn(v) : null;
        const d = document.createElement('div');
        d.className = 'cs-item' + (sel.has(v) ? ' selected' : '');
        if (icon) {{ const img=document.createElement('img'); img.className='cs-logo'; img.src=icon; img.alt=''; d.appendChild(img); }}
        const lbl=document.createElement('span'); lbl.className='cs-lbl'; lbl.textContent=v; d.appendChild(lbl);
        const chk=document.createElement('div'); chk.className='cs-check';
        chk.innerHTML='<svg class="cs-tick" viewBox="0 0 10 8" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M1 4l3 3 5-6"/></svg>';
        d.appendChild(chk);
        if (favOpts) {{
          const star = document.createElement('button');
          star.className = 'fav-star' + (favOpts.isFav(v) ? ' active' : '');
          star.textContent = favOpts.isFav(v) ? '★' : '☆';
          star.title = favOpts.isFav(v) ? 'Remove from My Cities' : 'Add to My Cities';
          star.addEventListener('mousedown', e => {{
            e.preventDefault(); e.stopPropagation();
            favOpts.toggle(v);
            star.textContent = favOpts.isFav(v) ? '★' : '☆';
            star.classList.toggle('active', favOpts.isFav(v));
            star.title = favOpts.isFav(v) ? 'Remove from My Cities' : 'Add to My Cities';
          }});
          d.appendChild(star);
        }}
        d.addEventListener('mousedown', e => {{
          e.preventDefault();
          sel.has(v) ? sel.delete(v) : sel.add(v);
          d.classList.toggle('selected', sel.has(v));
          badge.textContent = sel.size || '';
          badge.style.display = sel.size ? '' : 'none';
          btn.classList.toggle('active', sel.size > 0);
          render();
        }});
        frag.appendChild(d);
      }});
    }}
    list.appendChild(frag);
  }}

  btn.addEventListener('click', e => {{
    e.stopPropagation();
    const wasOpen = wrap.classList.contains('open');
    document.querySelectorAll('.custom-select.open').forEach(el => el.classList.remove('open'));
    if (!wasOpen) {{ wrap.classList.add('open'); renderItems(); if (searchEl) {{ searchEl.value=''; q=''; searchEl.focus(); }} }}
  }});
  if (searchEl) {{
    searchEl.addEventListener('keydown', e => e.stopPropagation());
    searchEl.addEventListener('input',   () => {{ q=searchEl.value; renderItems(); }});
  }}
  panel.addEventListener('click', e => e.stopPropagation());
  return {{ sel, refresh: renderItems }};
}}
document.addEventListener('click', () => document.querySelectorAll('.custom-select.open').forEach(el=>el.classList.remove('open')));

const PAGE_SIZE = 100;
let currentPage = 1;
let _usOnly = true;

const companyDrop = makeDropdown('cs-company', ()=>COMPANIES,                       v=>LOGOS[v], true);
const teamDrop    = makeDropdown('cs-team',    ()=>TEAMS,                           null,        false);
const expDrop     = makeDropdown('cs-exp',     ()=>EXPERIENCES,                     null,        false);
const cityDrop    = makeDropdown('cs-city',    ()=>Object.keys(CITY_COORDS).sort(), null,        false, {{isFav:isFavCity,toggle:city=>{{toggleFavCity(city);if(state.favCitiesOnly)render();}}}});

const state = {{ q:'', newOnly:false, favOnly:false, favCitiesOnly:false, sort:'foryou' }};

// ── Saved jobs storage ──
function getSavedList()   {{ return JSON.parse(localStorage.getItem('swipe_saved') || '[]'); }}
function getSaved()       {{ return new Set(getSavedList()); }}
function getDiscarded()   {{ return new Set(JSON.parse(localStorage.getItem('swipe_discarded') || '[]')); }}
function addSaved(id)     {{ const s=getSavedList().filter(x=>x!==id); s.push(id); localStorage.setItem('swipe_saved',JSON.stringify(s)); }}
function removeSaved(id)  {{ const s=getSavedList().filter(x=>x!==id); localStorage.setItem('swipe_saved',JSON.stringify(s)); }}
function addDiscarded(id) {{ const s=[...getDiscarded()]; if(!s.includes(id)) s.push(id); localStorage.setItem('swipe_discarded',JSON.stringify(s)); }}

// ── Applied jobs storage ──
function getAppliedList()  {{ return JSON.parse(localStorage.getItem('swipe_applied') || '[]'); }}
function getApplied()      {{ return new Set(getAppliedList()); }}
function addApplied(id)    {{ const s=getAppliedList().filter(x=>x!==id); s.push(id); localStorage.setItem('swipe_applied',JSON.stringify(s)); }}
function removeApplied(id) {{ const s=getAppliedList().filter(x=>x!==id); localStorage.setItem('swipe_applied',JSON.stringify(s)); }}

// ── Saved/applied snapshots ──
// JOBS only holds open jobs, so a saved/applied job vanishes from it once its company
// delists it. Keep a copy of each saved/applied job in localStorage so those tabs
// (and the applied profile) still have it without fetching the whole archive.
function getSnapshots() {{
  try {{ return JSON.parse(localStorage.getItem('job_snapshots') || '{{}}'); }} catch (e) {{ return {{}}; }}
}}
function syncSnapshots() {{
  const keep = new Set([...getSavedList(), ...getAppliedList()]);
  const old = getSnapshots(), out = {{}};
  for (const j of JOBS)            if (keep.has(j.role_id)) out[j.role_id] = j;
  for (const j of _loadedArchived) if (keep.has(j.role_id) && !out[j.role_id]) out[j.role_id] = j;
  for (const id of keep)           if (!out[id] && old[id]) out[id] = old[id];
  try {{ localStorage.setItem('job_snapshots', JSON.stringify(out)); }} catch (e) {{}}
  return out;
}}
let _snapshots = syncSnapshots();
// Saved/applied jobs that are no longer open.
function trackedArchived() {{ return Object.values(_snapshots).filter(j => !JOB_IDS.has(j.role_id)); }}
function hasUnresolvedTracked() {{
  return [...getSavedList(), ...getAppliedList()].some(id => !JOB_IDS.has(id) && !_snapshots[id]);
}}

// ── Applied-jobs learning: bias For You scoring toward what you actually apply to.
// Runs entirely client-side at page load / on every apply — no server round trip
// needed, so tonight's freshly-scraped jobs get scored against today's profile
// the moment the page opens, no separate "training" build step required.
const APPLIED_STOPWORDS = new Set(['the','and','for','with','from','into','your','you','our','are','was','were','this','that','will','who','all','any','new']);
function tokenizeTitle(title) {{
  return (title || '').toLowerCase().replace(/[^a-z0-9\\s]/g, ' ').split(/\\s+/)
    .filter(w => w.length >= 3 && !APPLIED_STOPWORDS.has(w));
}}
function buildAppliedProfile() {{
  const appliedIds = getApplied();
  const profile = {{ words: {{}}, companies: {{}}, teams: {{}}, n: 0 }};
  JOBS.concat(trackedArchived()).forEach(j => {{
    if (!appliedIds.has(j.role_id)) return;
    profile.n++;
    tokenizeTitle(j.title).forEach(w => {{ profile.words[w] = (profile.words[w] || 0) + 1; }});
    if (j.company) profile.companies[j.company] = (profile.companies[j.company] || 0) + 1;
    if (j.team)    profile.teams[j.team]        = (profile.teams[j.team]        || 0) + 1;
  }});
  return profile;
}}
let appliedProfile = buildAppliedProfile();
function refreshAppliedProfile() {{ appliedProfile = buildAppliedProfile(); _scoreCache.clear(); }}
// Needs >=3 applied jobs before trusting the signal — one data point is noise, not taste.
function personalizedBonus(j) {{
  if (appliedProfile.n < 3) return 0;
  let bonus = 0;
  const seen = new Set();
  tokenizeTitle(j.title).forEach(w => {{
    if (appliedProfile.words[w] && !seen.has(w)) {{
      seen.add(w);
      bonus += Math.min(5, appliedProfile.words[w] * 2);
    }}
  }});
  bonus = Math.min(25, bonus);
  if (j.company && appliedProfile.companies[j.company]) bonus += 8;
  if (j.team    && appliedProfile.teams[j.team])         bonus += 6;
  return Math.min(35, bonus);
}}

// ── Favorite companies storage ──
function getFavs()       {{ return new Set(JSON.parse(localStorage.getItem('fav_companies') || '[]')); }}
function setFavs(s)      {{ localStorage.setItem('fav_companies', JSON.stringify([...s])); }}
function isFav(company)  {{ return getFavs().has(company); }}
function toggleFav(company) {{
  const s = getFavs();
  s.has(company) ? s.delete(company) : s.add(company);
  setFavs(s);
  updateFavPill();
}}
function updateFavPill() {{
  const n = getFavs().size;
  const cnt = document.getElementById('fav-count');
  cnt.textContent = n;
  cnt.style.display = n > 0 ? '' : 'none';
  document.getElementById('pill-fav').classList.toggle('active', state.favOnly);
}}

// ── Favorite cities storage ──
function getFavCities()      {{ return new Set(JSON.parse(localStorage.getItem('fav_cities') || '[]')); }}
function setFavCities(s)     {{ localStorage.setItem('fav_cities', JSON.stringify([...s])); }}
function isFavCity(city)     {{ return getFavCities().has(city); }}
function toggleFavCity(city) {{
  const s = getFavCities();
  s.has(city) ? s.delete(city) : s.add(city);
  setFavCities(s);
  updateFavCitiesPill();
}}
function updateFavCitiesPill() {{
  const n = getFavCities().size;
  const cnt = document.getElementById('fav-cities-count');
  cnt.textContent = n;
  cnt.style.display = n > 0 ? '' : 'none';
  document.getElementById('pill-fav-cities').classList.toggle('active', state.favCitiesOnly);
}}

function updateHiddenCount() {{
  const n = getDiscarded().size;
  const el = document.getElementById('hidden-label');
  if (!el) return;
  if (n > 0) {{
    el.innerHTML = n + ' hidden · <a href="#" id="clear-hidden" style="color:var(--blue)">clear</a>';
    const cl = document.getElementById('clear-hidden');
    if (cl) cl.addEventListener('click', e => {{
      e.preventDefault();
      localStorage.removeItem('swipe_discarded');
      el.innerHTML = '';
      render();
    }});
  }} else {{
    el.innerHTML = '';
  }}
}}

const HIDDEN_TITLES = /\b(retail\s+sales|sales\s+associate|cashier|store\s+(manager|associate|leader|supervisor)|sales\s+rep(resentative)?|retail\s+associate|floor\s+(associate|supervisor)|merchandise|barista|bank\s+teller|teller\b|park\s+ranger|trail\s+crew|visitor\s+services|law\s+enforcement\s+ranger)\b/i;

function filtered() {{
  const _savedOnly   = state.sort === 'saved';
  const _appliedOnly = state.sort === 'applied';
  const _discarded = (_savedOnly || _appliedOnly) ? new Set() : getDiscarded();
  const _saved     = _savedOnly            ? getSaved()     : null;
  const _applied   = _appliedOnly          ? getApplied()   : null;
  const _favs      = state.favOnly         ? getFavs()      : null;
  const _favCities  = state.favCitiesOnly  ? getFavCities() : null;
  const src = state.sort === 'archive'        ? ARCHIVE
            : (_savedOnly || _appliedOnly)    ? JOBS.concat(trackedArchived())
            :                                   JOBS;
  return src.filter(j => {{
    if (HIDDEN_TITLES.test(j.title)) return false;
    if (_discarded.has(j.role_id))                                          return false;
    if (state.q              && !j.title.toLowerCase().includes(state.q) && !(j.company||'').toLowerCase().includes(state.q)) return false;
    if (state.newOnly        && !j.is_new)                                 return false;
    if (_savedOnly            && !_saved.has(j.role_id))                   return false;
    if (_appliedOnly          && !_applied.has(j.role_id))                 return false;
    if (state.favOnly        && !_favs.has(j.company))                    return false;
    if (state.favCitiesOnly) {{
      const fc = _favCities;
      if (fc.size > 0) {{
        const locs = getLocations(j);
        if (!locs.some(n => fc.has(n.display))) return false;
      }}
    }}
    if (companyDrop.sel.size && !companyDrop.sel.has(j.company))          return false;
    if (teamDrop.sel.size    && !teamDrop.sel.has(j.team))                return false;
    if (expDrop.sel.size     && !expDrop.sel.has(j.experience))           return false;
    if (state.sort === 'foryou' && getApplied().has(j.role_id))           return false;
    if (state.sort === 'foryou' && scoreJob(j) < 20)                      return false;
    if (_usOnly) {{
      const locs = getLocations(j);
      if (locs.length > 0 && !locs.some(n => n.isUS)) return false;
    }}
    if (cityDrop.sel.size) {{
      const miles = parseInt(document.getElementById('radius-miles').value) || 0;
      const locs = getLocations(j);
      if (miles) {{
        const inRange = [...cityDrop.sel].some(city => {{
          const center = CITY_COORDS[city];
          if (!center) return false;
          return locs.some(n => {{
            const c = CITY_COORDS[n.display];
            return c && haversine(center.lat, center.lon, c.lat, c.lon) <= miles;
          }});
        }});
        if (!inRange) return false;
      }} else {{
        const hasMatch = [...cityDrop.sel].some(city =>
          locs.some(n => n.display.toLowerCase() === city.toLowerCase())
        );
        if (!hasMatch) return false;
      }}
    }}
    return true;
  }});
}}

function parseDate(str) {{
  if (!str) return 0;
  // relative: "21 minutes ago", "an hour ago", "2 days ago", "a week ago"
  const rel = str.toLowerCase();
  const now = Date.now();
  const n = m => {{ const x = rel.match(m); return x ? (x[1]==='a'||x[1]==='an' ? 1 : parseInt(x[1])) : null; }};
  if (rel.includes('yesterday')) return now - 86400*1000;
  if (rel.includes('today') || rel.includes('just posted')) return now;
  if (rel.includes('minute'))  {{ const v=n(/(\\d+|a|an)\\s+minute/); if(v) return now - v*60*1000; }}
  if (rel.includes('hour'))    {{ const v=n(/(\\d+|a|an)\\s+hour/);   if(v) return now - v*3600*1000; }}
  if (rel.includes('day'))     {{ const v=n(/(\\d+|a|an)\\s+day/);    if(v) return now - v*86400*1000; }}
  if (rel.includes('week'))    {{ const v=n(/(\\d+|a|an)\\s+week/);   if(v) return now - v*7*86400*1000; }}
  if (rel.includes('month'))   {{ const v=n(/(\\d+|a|an)\\s+month/);  if(v) return now - v*30*86400*1000; }}
  // bare "YYYY-MM-DD" parses as UTC midnight in JS, unlike "Apr 19, 2026" which
  // parses as local midnight — that mismatch shifts it a day in timezones behind
  // UTC, splitting same-day jobs across different day-buckets. Parse it as a
  // local date explicitly so it lines up with the formatted-string dates.
  const isoMatch = str.match(/^(\d{{4}})-(\d{{2}})-(\d{{2}})$/);
  if (isoMatch) {{
    const dLocal = new Date(+isoMatch[1], +isoMatch[2] - 1, +isoMatch[3]);
    return dLocal.getTime() > Date.now() ? 0 : dLocal.getTime();
  }}
  // absolute: "Apr 19, 2026"
  const d = new Date(str);
  if (isNaN(d)) return 0;
  // future dates (e.g. expiration fields) treated as unknown
  return d.getTime() > Date.now() ? 0 : d.getTime();
}}

function fmtDate(ts) {{
  if (!ts) return null;
  const d = new Date(ts);
  return (d.getMonth() + 1) + '/' + d.getDate();
}}

function sorted(arr) {{
  if (state.sort === 'title')  return [...arr].sort((a,b)=>a.title.localeCompare(b.title));
  if (state.sort === 'saved') {{
    const order = getSavedList();
    return [...arr].sort((a,b) => order.indexOf(b.role_id) - order.indexOf(a.role_id));
  }}
  if (state.sort === 'applied') {{
    const order = getAppliedList();
    return [...arr].sort((a,b) => order.indexOf(b.role_id) - order.indexOf(a.role_id));
  }}
  if (state.sort === 'foryou') return [...arr].sort((a,b) => {{
    const ta = parseDate(a.posted_date) || parseDate(a.first_seen);
    const tb = parseDate(b.posted_date) || parseDate(b.first_seen);
    return tb - ta || scoreJob(b) - scoreJob(a) || a.title.localeCompare(b.title);
  }});
  return [...arr].sort((a,b) => {{
    const ta = parseDate(a.posted_date) || parseDate(a.first_seen);
    const tb = parseDate(b.posted_date) || parseDate(b.first_seen);
    return tb - ta || a.title.localeCompare(b.title);
  }});
}}

const grid       = document.getElementById('grid');
const label      = document.getElementById('count-label');
const pagination = document.getElementById('pagination');

function _dayKey(j) {{
  const ts = parseDate(j.posted_date) || parseDate(j.first_seen);
  if (!ts) return null;
  const d = new Date(ts);
  return d.getFullYear() + '-' + d.getMonth() + '-' + d.getDate();
}}

function renderPagination(total, totalPages) {{
  pagination.innerHTML = '';
  if (totalPages <= 1) return;

  const start = (currentPage - 1) * PAGE_SIZE + 1;
  const end   = Math.min(currentPage * PAGE_SIZE, total);

  const prev = document.createElement('button');
  prev.className = 'page-btn'; prev.textContent = '‹ Prev';
  prev.disabled = currentPage === 1;
  prev.addEventListener('click', () => {{ currentPage--; renderPage(window._lastList); scrollToGrid(); }});
  pagination.appendChild(prev);

  // window around current page
  const delta = 2;
  const pages = new Set([1, totalPages]);
  for (let i = Math.max(2, currentPage-delta); i <= Math.min(totalPages-1, currentPage+delta); i++) pages.add(i);
  let last = 0;
  [...pages].sort((a,b)=>a-b).forEach(p => {{
    if (last && p - last > 1) {{
      const dots = document.createElement('span');
      dots.className = 'page-label'; dots.textContent = '…';
      pagination.appendChild(dots);
    }}
    const btn = document.createElement('button');
    btn.className = 'page-btn' + (p === currentPage ? ' active' : '');
    btn.textContent = p;
    btn.addEventListener('click', () => {{ currentPage = p; renderPage(window._lastList); scrollToGrid(); }});
    pagination.appendChild(btn);
    last = p;
  }});

  const next = document.createElement('button');
  next.className = 'page-btn'; next.textContent = 'Next ›';
  next.disabled = currentPage === totalPages;
  next.addEventListener('click', () => {{ currentPage++; renderPage(window._lastList); scrollToGrid(); }});
  pagination.appendChild(next);
}}

function scrollToGrid() {{
  grid.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
}}

function renderPage(list) {{
  window._lastList = list;
  const totalPages = Math.ceil(list.length / PAGE_SIZE);
  currentPage = Math.max(1, Math.min(currentPage, totalPages || 1));

  const start = (currentPage - 1) * PAGE_SIZE;
  const page  = list.slice(start, start + PAGE_SIZE);
  const end   = start + page.length;

  if (list.length === 0) {{
    label.textContent = '0 jobs shown';
  }} else {{
    label.textContent = `Showing ${{(start+1).toLocaleString()}}–${{end.toLocaleString()}} of ${{list.length.toLocaleString()}} job${{list.length!==1?'s':''}}`;
  }}

  const dayLabelEl = document.getElementById('current-day-label');
  const nextDayBtn = document.getElementById('next-day-btn');
  if ((state.sort === 'newest' || state.sort === 'foryou') && list.length) {{
    const curTs = parseDate(list[start].posted_date) || parseDate(list[start].first_seen);
    dayLabelEl.textContent = curTs ? `· Viewing ${{fmtDate(curTs)}}` : '';
    const curDay = _dayKey(list[start]);
    let nextIdx = -1;
    for (let i = start; i < list.length; i++) {{
      if (_dayKey(list[i]) !== curDay) {{ nextIdx = i; break; }}
    }}
    if (nextIdx !== -1) {{
      // if the transition already falls on/before this page, the whole next page
      // is guaranteed to start on the new day — jumping to the transition's own
      // page would just reload the page you're already on.
      const targetPage = Math.max(Math.floor(nextIdx / PAGE_SIZE) + 1, currentPage + 1);
      nextDayBtn.style.display = '';
      nextDayBtn.onclick = () => {{ currentPage = targetPage; renderPage(window._lastList); scrollToGrid(); }};
    }} else {{
      nextDayBtn.style.display = 'none';
      nextDayBtn.onclick = null;
    }}
  }} else {{
    dayLabelEl.textContent = '';
    nextDayBtn.style.display = 'none';
    nextDayBtn.onclick = null;
  }}

  grid.innerHTML = '';
  if (!page.length) {{
    grid.innerHTML = '<div class="no-results">No jobs match your filters.</div>';
    renderPagination(0, 0);
    return;
  }}
  const frag = document.createDocumentFragment();
  const head = document.createElement('div');
  head.className = 'job-head';
  head.innerHTML = '<span></span><span>Company</span><span>Title</span><span>Location</span><span>Posted</span><span></span><span class="h-score">Match</span>';
  frag.appendChild(head);
  page.forEach(j => {{
    const logoSrc = LOGOS[j.company];
    const scDetail = scoreJobDetailed(j);
    const sc = scDetail ? scDetail.score : -1;
    const matchColor = sc >= 70 ? '#34c759' : sc >= 40 ? '#ff9500' : '#8e8e93';
    const scTitle = scDetail
      ? scDetail.breakdown.map(b => `${{b.label}}: ${{b.delta >= 0 ? '+' : ''}}${{b.delta}}`).join('\\n')
        + `\\n—\\nTotal: ${{sc}}%`
      : '';
    const isSaved = getSaved().has(j.role_id);
    const isApplied = getApplied().has(j.role_id);
    const _postTs = parseDate(j.posted_date);
    const _seenTs = parseDate(j.first_seen);
    const _goneStr = !JOB_IDS.has(j.role_id) && j.last_seen
      ? `<span class="gone" title="Last listed ${{j.last_seen}}">gone ${{fmtDate(parseDate(j.last_seen)) || j.last_seen}}</span>`
      : '';
    const _dateStr = (j.posted_date
      ? `<span title="Posted ${{j.posted_date}}">${{fmtDate(_postTs) || j.posted_date}}</span>`
      : `<span class="first-seen" title="No posted date — first seen ${{j.first_seen}}">${{fmtDate(_seenTs) || j.first_seen}}</span>`)
      + _goneStr;
    const _locs = (j.location || '').split(/\\s*[|/;]\\s*/).filter(Boolean);
    const _cityStr = _locs.length > 1 ? `${{_locs[0]}} +${{_locs.length - 1}}` : (_locs[0] || '');
    const _sub = [j.team, j.experience].filter(Boolean).join(' · ');
    const _isNew = (()=>{{const pts=parseDate(j.posted_date);const rec=!j.posted_date||(pts>0&&(Date.now()-pts)<14*86400*1000);return j.is_new&&rec;}})();
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
      ${{logoSrc ? `<img class="logo" src="${{logoSrc}}" alt=""/>` : '<span class="logo"></span>'}}
      <span class="company-label" title="${{j.company}}">${{j.company}}</span>
      <div class="card-title">
        ${{_isNew ? '<span class="new-badge">NEW</span>' : ''}}<a href="${{j.url}}" target="_blank" rel="noopener">${{j.title}}</a>
        ${{_sub ? `<div class="card-sub" title="${{_sub.replace(/"/g,'&quot;')}}">${{_sub}}</div>` : ''}}
      </div>
      <div class="card-city" title="${{(j.location || '').replace(/"/g,'&quot;')}}">${{_cityStr}}</div>
      <div class="card-date">${{_dateStr}}</div>
      <div class="card-actions">
        <button class="card-hide-btn" title="Hide this job">✕</button>
        <button class="card-star-btn${{isSaved ? ' saved' : ''}}" title="${{isSaved ? 'Remove from Saved' : 'Save'}}">${{isSaved ? '★' : '☆'}}</button>
        <button class="card-apply-btn${{isApplied ? ' applied' : ''}}" title="${{isApplied ? 'Remove from Applied' : 'Mark as Applied'}}">➔</button>
      </div>
      <div class="card-score">${{sc >= 0 ? `<span class="match-badge" style="background:${{matchColor}}" title="${{scTitle.replace(/"/g,'&quot;')}}">${{sc}}%</span>` : ''}}</div>
    `;
    card.querySelector('.card-star-btn').addEventListener('click', e => {{
      e.stopPropagation();
      const btn = e.currentTarget;
      if (getSaved().has(j.role_id)) {{
        removeSaved(j.role_id);
        btn.classList.remove('saved');
        btn.textContent = '☆';
        btn.title = 'Save';
      }} else {{
        addSaved(j.role_id);
        btn.classList.add('saved');
        btn.textContent = '★';
        btn.title = 'Remove from Saved';
      }}
      if (state.sort === 'saved') render();
    }});
    card.querySelector('.card-apply-btn').addEventListener('click', e => {{
      e.stopPropagation();
      const btn = e.currentTarget;
      if (getApplied().has(j.role_id)) {{
        removeApplied(j.role_id);
        btn.classList.remove('applied');
        btn.title = 'Mark as Applied';
      }} else {{
        addApplied(j.role_id);
        if (getSaved().has(j.role_id)) {{
          removeSaved(j.role_id);
          const starBtn = card.querySelector('.card-star-btn');
          starBtn.classList.remove('saved');
          starBtn.textContent = '☆';
          starBtn.title = 'Save';
        }}
        btn.classList.add('applied');
        btn.title = 'Remove from Applied';
      }}
      refreshAppliedProfile();
      if (state.sort === 'saved' || state.sort === 'applied' || state.sort === 'foryou') render();
    }});
    card.querySelector('.card-hide-btn').addEventListener('click', e => {{
      e.stopPropagation();
      addDiscarded(j.role_id);
      card.style.transition = 'opacity 0.2s';
      card.style.opacity = '0';
      setTimeout(() => card.remove(), 200);
      updateHiddenCount();
    }});
    frag.appendChild(card);
  }});
  grid.appendChild(frag);
  renderPagination(list.length, totalPages);
}}

function render() {{
  _snapshots = syncSnapshots();
  currentPage = 1;
  renderPage(sorted(filtered()));
  updateHiddenCount();
}}

// ── Archive tab ──
const archiveSel = document.getElementById('archive-month');
function fmtMonth(m) {{
  const [y, mo] = m.split('-').map(Number);
  return mo ? new Date(y, mo - 1, 1).toLocaleString('en-US', {{ month: 'short', year: 'numeric' }}) : m;
}}
archiveSel.innerHTML = ARCHIVE_MONTHS.length
  ? ARCHIVE_MONTHS.map(m => `<option value="${{m.month}}">Found ${{fmtMonth(m.month)}} (${{m.count.toLocaleString()}})</option>`).join('')
  : '<option value="">No archived jobs yet</option>';
async function showArchiveMonth() {{
  const month = archiveSel.value;
  ARCHIVE = [];
  if (!month) {{ render(); return; }}
  grid.innerHTML = '';
  pagination.innerHTML = '';
  label.textContent = `Loading ${{fmtMonth(month)}} archive…`;
  try {{
    const jobs = await loadArchiveMonth(month);
    if (state.sort !== 'archive' || archiveSel.value !== month) return;  // user moved on
    ARCHIVE = jobs;
    render();
  }} catch (e) {{
    if (state.sort === 'archive') label.textContent = `Couldn't load archive (${{e.message}})`;
  }}
}}
archiveSel.addEventListener('change', showArchiveMonth);

// Saved/applied jobs archived before this browser stored a snapshot of them: find
// them in the archive once, then the snapshots cover it from then on.
if (ARCHIVE_MONTHS.length && hasUnresolvedTracked()) {{
  loadAllArchive().then(() => {{
    _snapshots = syncSnapshots();
    refreshAppliedProfile();
    if (state.sort !== 'archive') render();
  }}).catch(() => {{}});
}}

let _qDebounce = null;
document.getElementById('q').addEventListener('input', e => {{
  const v = e.target.value.trim().toLowerCase();
  clearTimeout(_qDebounce);
  _qDebounce = setTimeout(() => {{ state.q = v.length >= 3 ? v : ''; render(); }}, 300);
}});
document.querySelectorAll('[data-new]').forEach(b => b.addEventListener('click', () => {{
  document.querySelectorAll('[data-new]').forEach(x=>x.classList.remove('active'));
  b.classList.add('active'); state.newOnly = b.dataset.new === 'new'; render();
}}));
document.querySelectorAll('[data-region]').forEach(b => b.addEventListener('click', () => {{
  document.querySelectorAll('[data-region]').forEach(x=>x.classList.remove('active'));
  b.classList.add('active');
  _usOnly = b.dataset.region === 'us';
  render();
}}));
document.querySelectorAll('[data-sort]').forEach(b => b.addEventListener('click', () => {{
  document.querySelectorAll('[data-sort]').forEach(x=>x.classList.remove('active'));
  b.classList.add('active'); state.sort = b.dataset.sort;
  archiveSel.style.display = state.sort === 'archive' ? '' : 'none';
  if (state.sort === 'archive') showArchiveMonth(); else render();
}}));

document.getElementById('radius-miles').addEventListener('change', function() {{
  this.classList.toggle('active', !!this.value);
  render();
}});

// ── "My Companies" pill ──
document.getElementById('pill-fav').addEventListener('click', function() {{
  state.favOnly = !state.favOnly;
  this.classList.toggle('active', state.favOnly);
  render();
}});
updateFavPill();
updateFavCitiesPill();

// ── "My Cities" pill ──
document.getElementById('pill-fav-cities').addEventListener('click', function() {{
  state.favCitiesOnly = !state.favCitiesOnly;
  this.classList.toggle('active', state.favCitiesOnly);
  render();
}});

render();

// ── Export CSV ──
function exportCSV() {{
  const rows = sorted(filtered());
  const header = ['Title','Company','Team','Location','Experience','Posted','URL'];
  const lines = rows.map(j => [
    j.title, j.company, j.team||'', (j.location||'').replace(/\\n/g,' '),
    j.experience||'', j.posted_date||j.first_seen||'', j.url
  ].map(v => '"' + String(v).replace(/"/g,'""') + '"').join(','));
  const csv = [header.join(','), ...lines].join('\\n');
  const blob = new Blob([csv], {{type:'text/csv'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'dream-companies-jobs.csv';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(a.href);
}}
document.getElementById('export-btn').addEventListener('click', exportCSV);

// ── Stats panel ──
(function() {{
  let statsSort = {{ col: 'total', dir: 1 }};  // dir:1 = desc for numbers (bv-av)
  let statsQ = '';

  function buildStatsData() {{
    const now = Date.now();
    const ms24h = 86400 * 1000;
    const map = {{}};
    for (const j of JOBS) {{
      const c = j.company || 'Unknown';
      if (!map[c]) map[c] = {{ company: c, total: 0, newToday: 0, posted24h: 0 }};
      map[c].total++;
      if (j.is_new) map[c].newToday++;
      const pd = parseDate(j.posted_date);
      if (pd && (now - pd) < ms24h * 2) map[c].posted24h++;
    }}
    const rows = Object.values(map);
    rows.forEach(r => {{
      if (r.posted24h > 0)        {{ r.statusVal = 2; r.statusIcon = '🟢'; r.statusTitle = 'Active — posted in last 48h'; }}
      else if (r.newToday > 0)    {{ r.statusVal = 1; r.statusIcon = '🟡'; r.statusTitle = 'Stale — scraper ran but no recent postings'; }}
      else                        {{ r.statusVal = 0; r.statusIcon = '🔴'; r.statusTitle = 'No recent activity — scraper may be broken'; }}
    }});
    return rows;
  }}

  function renderStats() {{
    const rows = buildStatsData()
      .filter(r => !statsQ || r.company.toLowerCase().includes(statsQ))
      .sort((a, b) => {{
        const av = statsSort.col === 'company' ? a.company : statsSort.col === 'status' ? a.statusVal : a[statsSort.col === 'new' ? 'newToday' : statsSort.col === 'posted' ? 'posted24h' : 'total'];
        const bv = statsSort.col === 'company' ? b.company : statsSort.col === 'status' ? b.statusVal : b[statsSort.col === 'new' ? 'newToday' : statsSort.col === 'posted' ? 'posted24h' : 'total'];
        if (typeof av === 'string') return statsSort.dir * av.localeCompare(bv);
        return statsSort.dir * (bv - av);
      }});

    const tbody = document.getElementById('stats-tbody');
    tbody.innerHTML = rows.map(r => {{
      const logo = LOGOS[r.company] ? `<img class="stats-logo" src="${{LOGOS[r.company]}}" alt=""/>` : '<span style="width:22px;display:inline-block"></span>';
      return `<tr onclick="companyDrop.sel.clear();companyDrop.sel.add('${{r.company.replace(/'/g,"\\'")}}');document.getElementById('stats-overlay').classList.remove('open');render();">
        <td><div class="stats-company-cell">${{logo}}<span>${{r.company}}</span></div></td>
        <td class="stats-total">${{r.total.toLocaleString()}}</td>
        <td class="stats-new${{r.newToday ? '' : ' zero'}}">${{r.newToday || '—'}}</td>
        <td class="stats-posted${{r.posted24h ? '' : ' zero'}}">${{r.posted24h || '—'}}</td>
        <td class="stats-status" title="${{r.statusTitle}}">${{r.statusIcon}}</td>
      </tr>`;
    }}).join('');

    document.getElementById('stats-footer').textContent = `${{rows.length}} companies · click a row to filter`;

    // Update sort indicators
    document.querySelectorAll('.stats-table thead th').forEach(th => {{
      th.classList.remove('sort-asc','sort-desc');
      if (th.dataset.col === statsSort.col) {{
        // numbers: dir=1→descending, dir=-1→ascending; company: dir=1→ascending
        const isNum = th.dataset.col !== 'company';
        th.classList.add((isNum ? statsSort.dir === 1 : statsSort.dir === 1) ? 'sort-desc' : 'sort-asc');
      }}
    }});
  }}

  document.getElementById('stats-btn').addEventListener('click', () => {{
    document.getElementById('stats-overlay').classList.add('open');
    renderStats();
  }});
  document.getElementById('stats-close').addEventListener('click', () => {{
    document.getElementById('stats-overlay').classList.remove('open');
  }});
  document.getElementById('stats-overlay').addEventListener('click', e => {{
    if (e.target === document.getElementById('stats-overlay'))
      document.getElementById('stats-overlay').classList.remove('open');
  }});
  document.getElementById('stats-search').addEventListener('input', function() {{
    statsQ = this.value.toLowerCase();
    renderStats();
  }});
  document.querySelectorAll('.stats-table thead th').forEach(th => {{
    th.addEventListener('click', () => {{
      if (statsSort.col === th.dataset.col) {{
        statsSort.dir *= -1;
      }} else {{
        statsSort = {{ col: th.dataset.col, dir: th.dataset.col === 'company' ? 1 : 1 }};
      }}
      renderStats();
    }});
  }});
}})();
</script>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"Built index.html — {len(active_jobs)} active jobs, {new_count} new; "
      f"{len(archived_jobs)} archived in {len(archive_months)} {ARCHIVE_DIR}/ files")
if not _args.no_open:
    webbrowser.open("index.html")

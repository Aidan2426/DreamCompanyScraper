"""
Reads jobs.json and generates index.html.
Run: python build.py
"""
import json
import os
import re
import time
import urllib.request
import urllib.parse
import webbrowser

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

def _geocode_cities(city_counts, cache_file='city_coords.json'):
    cache = {}
    if os.path.exists(cache_file):
        with open(cache_file, encoding='utf-8') as f:
            try:
                cache = json.load(f)
            except Exception:
                pass
    to_geocode = [c for c in city_counts if c not in cache]
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
experiences = sorted({j["experience"] for j in jobs if j.get("experience")})

city_counts  = _extract_job_us_cities(jobs)
city_counts  = {c: n for c, n in city_counts.items() if n >= 2}
city_coords  = _geocode_cities(city_counts)

jobs_json         = json.dumps(jobs,         ensure_ascii=False)
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
  <title>Dream Jobs</title>
  <link rel="icon" type="image/jpeg" href="free-simpmle-star-clipart-01-1.jpg"/>
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

    /* ── Nav ── */
    nav {{
      position: sticky; top: 0; z-index: 100;
      height: 52px; display: flex; align-items: center; justify-content: space-between;
      padding: 0 28px;
      background: rgba(255,255,255,0.85);
      backdrop-filter: saturate(180%) blur(20px);
      border-bottom: 1px solid #d2d2d7;
    }}
    .nav-brand {{ font-size: 17px; font-weight: 700; letter-spacing: -0.3px; }}
    .nav-meta  {{ font-size: 13px; color: var(--muted); }}

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
      position: sticky; top: 52px; z-index: 90;
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
    .radius-wrap {{
      display: inline-flex; align-items: center; gap: 4px;
    }}
    .radius-city-input {{
      font-size: 12.5px; padding: 5px 12px;
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.10);
      border-radius: 980px; color: rgba(255,255,255,0.55);
      outline: none; width: 138px; font-weight: 500;
      transition: all 0.15s;
    }}
    .radius-city-input::placeholder {{ color: rgba(255,255,255,0.3); }}
    .radius-city-input:focus {{ background: rgba(255,255,255,0.09); border-color: rgba(0,113,227,0.65); color: #fff; }}
    .radius-city-input.active {{ border-color: var(--blue); color: #fff; background: rgba(0,113,227,0.10); }}
    .radius-clear {{
      background: none; border: none; cursor: pointer; padding: 0 2px;
      color: rgba(255,255,255,0.4); font-size: 13px; line-height: 1;
      transition: color 0.15s;
    }}
    .radius-clear:hover {{ color: #fff; }}
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
      max-width: 1100px; margin: 28px auto 0; padding: 0 28px;
      font-size: 13px; color: var(--muted);
    }}

    /* ── Grid ── */
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 16px; max-width: 1100px;
      margin: 16px auto 80px; padding: 0 28px;
    }}

    /* ── Card ── */
    .card {{
      background: var(--white); border-radius: 16px; padding: 22px;
      display: flex; flex-direction: column; gap: 10px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.07);
      transition: box-shadow 0.2s, transform 0.2s;
    }}
    .card:hover {{ box-shadow: 0 6px 24px rgba(0,0,0,0.12); transform: translateY(-2px); }}

    .card-top {{
      display: flex; align-items: center; gap: 10px;
    }}
    .logo {{
      width: 22px; height: 22px; object-fit: contain; flex-shrink: 0;
    }}
    .company-label {{ font-size: 12px; color: var(--muted); font-weight: 500; }}
    .card-top-right {{ margin-left: auto; display: flex; gap: 4px; align-items: center; }}
    .new-badge {{
      font-size: 10px; font-weight: 700;
      background: #34c759; color: #fff;
      border-radius: 5px; padding: 2px 7px; letter-spacing: 0.4px;
    }}
    .match-badge {{
      font-size: 10px; font-weight: 700; color: #fff;
      border-radius: 5px; padding: 2px 7px; letter-spacing: 0.3px;
    }}

    .card-title {{
      font-size: 15px; font-weight: 600; line-height: 1.35;
    }}
    .card-title a {{
      color: inherit; text-decoration: none;
    }}
    .card-title a:hover {{ color: var(--blue); }}

    .tags {{ display: flex; flex-wrap: wrap; gap: 5px; }}
    .tag {{
      font-size: 11px; font-weight: 500; border-radius: 6px; padding: 2px 8px;
      background: #f5f5f7; border: 1px solid #e5e5ea; color: #3a3a3c;
    }}
    .tag-team  {{ background: #e8f0fe; border-color: #c5d4f8; color: #1a3a8f; }}
    .tag-exp   {{ background: #fef3e2; border-color: #fcd58a; color: #7a4800; }}
    .tag-loc   {{ background: #f5f5f7; }}

    .card-date {{ font-size: 12px; color: #8e8e93; margin-top: auto; }}

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

    /* ── Swiper modal ── */
    .swiper-overlay {{
      display: none; position: fixed; inset: 0; z-index: 1000;
      background: rgba(0,0,0,0.85); backdrop-filter: blur(6px);
      flex-direction: column; align-items: center; justify-content: center;
    }}
    .swiper-overlay.open {{ display: flex; }}
    .swiper-header {{
      width: 100%; max-width: 420px; display: flex; align-items: center;
      justify-content: space-between; padding: 0 4px 16px;
    }}
    .swiper-header-left {{ display: flex; align-items: center; gap: 10px; }}
    .swiper-close {{
      background: none; border: none; color: rgba(255,255,255,0.5);
      font-size: 22px; cursor: pointer; line-height: 1; padding: 0;
    }}
    .swiper-close:hover {{ color: #fff; }}
    .swiper-progress {{ font-size: 13px; color: rgba(255,255,255,0.5); }}
    .swiper-saved-btn {{
      background: none; border: 1px solid rgba(255,255,255,0.2); border-radius: 20px;
      color: rgba(255,255,255,0.6); font-size: 12px; padding: 4px 12px; cursor: pointer;
    }}
    .swiper-saved-btn:hover {{ color: #fff; border-color: rgba(255,255,255,0.5); }}
    .swiper-stack {{
      width: 100%; max-width: 420px; height: 520px; position: relative;
    }}
    .swiper-card {{
      position: absolute; inset: 0; background: #1c1c1e; border-radius: 20px;
      padding: 28px 24px 24px; display: flex; flex-direction: column;
      user-select: none; touch-action: none; cursor: grab;
      box-shadow: 0 20px 60px rgba(0,0,0,0.5);
      transition: transform 0.08s ease;
    }}
    .swiper-card:active {{ cursor: grabbing; }}
    .swiper-card.swipe-left  {{ transition: transform 0.35s ease, opacity 0.35s ease; }}
    .swiper-card.swipe-right {{ transition: transform 0.35s ease, opacity 0.35s ease; }}
    .swiper-card-back {{
      position: absolute; inset: 0; background: #1c1c1e; border-radius: 20px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.5);
      transform: scale(0.96) translateY(8px); z-index: -1;
    }}
    .swiper-card-back2 {{
      position: absolute; inset: 0; background: #1c1c1e; border-radius: 20px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.5);
      transform: scale(0.92) translateY(16px); z-index: -2; opacity: 0.5;
    }}
    .swipe-indicator {{
      position: absolute; top: 24px; border-radius: 8px;
      font-size: 15px; font-weight: 800; padding: 6px 14px;
      opacity: 0; transition: opacity 0.1s; pointer-events: none;
      letter-spacing: 1px; text-transform: uppercase;
    }}
    .swipe-save-ind  {{ left: 20px;  background: rgba(52,199,89,0.25);  color: #34c759; border: 2px solid #34c759; }}
    .swipe-skip-ind  {{ right: 20px; background: rgba(255,59,48,0.25);  color: #ff3b30; border: 2px solid #ff3b30; }}
    .swiper-logo-wrap {{
      display: flex; flex-direction: column; align-items: center; margin-bottom: 18px;
    }}
    .swiper-logo {{
      width: 72px; height: 72px; object-fit: contain; border-radius: 14px;
      background: #2c2c2e; padding: 8px;
    }}
    .swiper-logo-placeholder {{
      width: 72px; height: 72px; border-radius: 14px;
      background: linear-gradient(135deg,#2c2c2e,#3a3a3c);
      display: flex; align-items: center; justify-content: center;
      font-size: 26px; font-weight: 700; color: rgba(255,255,255,0.4);
    }}
    .swiper-company {{ font-size: 12px; color: var(--muted); margin-top: 6px; letter-spacing: 0.5px; text-transform: uppercase; }}
    .swiper-title {{ font-size: 19px; font-weight: 700; color: #fff; text-align: center; margin-bottom: 16px; line-height: 1.3; }}
    .swiper-meta {{ display: flex; flex-direction: column; gap: 7px; flex: 1; }}
    .swiper-meta-row {{ display: flex; align-items: flex-start; gap: 8px; font-size: 13px; color: rgba(255,255,255,0.7); }}
    .swiper-meta-icon {{ font-size: 13px; min-width: 16px; text-align: center; }}
    .swiper-badges {{ display: flex; gap: 6px; margin-top: 6px; flex-wrap: wrap; justify-content: center; }}
    .swiper-badge-new  {{ background: var(--blue); color: #fff; border-radius: 6px; padding: 3px 9px; font-size: 11px; font-weight: 700; }}
    .swiper-badge-pct  {{ border-radius: 6px; padding: 3px 9px; font-size: 11px; font-weight: 700; color: #fff; }}
    .swiper-actions {{
      display: flex; gap: 16px; justify-content: center; margin-top: 20px;
    }}
    .swiper-btn {{
      width: 64px; height: 64px; border-radius: 50%; border: none; cursor: pointer;
      font-size: 26px; display: flex; align-items: center; justify-content: center;
      transition: transform 0.15s, box-shadow 0.15s;
    }}
    .swiper-btn:hover {{ transform: scale(1.1); }}
    .swiper-btn-skip {{ background: rgba(255,59,48,0.15); color: #ff3b30; }}
    .swiper-btn-save {{ background: rgba(52,199,89,0.15); color: #34c759; }}
    .swiper-done {{
      text-align: center; color: rgba(255,255,255,0.5);
      font-size: 16px; padding: 40px 20px;
    }}
    .swiper-done-title {{ font-size: 24px; color: #fff; margin-bottom: 10px; }}
    .card-save-btn {{
      background: none; border: none; cursor: pointer; padding: 2px 4px;
      font-size: 15px; color: rgba(255,255,255,0.45); line-height: 1;
      transition: color 0.15s, transform 0.15s; flex-shrink: 0;
    }}
    .card-save-btn:hover {{ color: #ff6b8a; transform: scale(1.2); }}
    .card-save-btn.saved {{ color: #ff6b8a; }}
    .pill-saved {{ position: relative; }}
    .pill-saved-count {{
      position: absolute; top: -6px; right: -6px;
      background: #34c759; color: #fff; border-radius: 8px;
      font-size: 10px; font-weight: 700; padding: 1px 5px; min-width: 16px; text-align: center;
    }}
  </style>
</head>
<body>

<nav>
  <span class="nav-brand"><img src="free-simpmle-star-clipart-01-1.jpg" style="height:26px;width:26px;object-fit:contain;vertical-align:middle;margin-right:7px;border-radius:4px;"/>Dream Jobs</span>
  <span class="nav-meta" id="nav-meta">{len(jobs)} jobs · {new_count} new today</span>
</nav>

<div class="hero">
  <h1>Dream Jobs</h1>
  <p>{len(jobs):,} jobs tracked{' · ' + str(new_count) + ' new today' if new_count else ''}{' · Updated ' + scraped_at if scraped_at else ''}</p>
</div>

<div class="controls-bar">
  <div class="search-wrap">
    <svg class="s-icon" viewBox="0 0 20 20"><circle cx="8.5" cy="8.5" r="5.5"/><line x1="13" y1="13" x2="18" y2="18"/></svg>
    <input class="search-input" id="q" type="search" placeholder="Search jobs…" autocomplete="off"/>
  </div>
  <div class="filter-strip">
    <button class="pill active" data-new="all">All</button>
    <button class="pill" data-new="new">✦ New</button>
    <button class="pill pill-saved" id="pill-saved" data-new="saved" style="display:none">♥ Saved<span class="pill-saved-count" id="saved-count">0</span></button>
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
    <div class="radius-wrap">
      <input class="radius-city-input" id="radius-city" type="text" placeholder="City, ST" list="city-datalist" autocomplete="off"/>
      <button class="radius-clear" id="radius-clear" title="Clear city" style="display:none">✕</button>
      <datalist id="city-datalist"></datalist>
      <select class="radius-select" id="radius-miles">
        <option value="">Any dist</option>
        <option value="25">25 mi</option>
        <option value="50">50 mi</option>
        <option value="100">100 mi</option>
        <option value="200">200 mi</option>
      </select>
    </div>
    <div class="custom-select" id="cs-exp">
      <button class="cs-btn"><span class="cs-btn-label">Level</span><span class="cs-badge"></span><svg class="cs-chevron" width="10" height="6" viewBox="0 0 10 6" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M1 1l4 4 4-4"/></svg></button>
      <div class="cs-panel"><div class="cs-list"></div></div>
    </div>
    <div class="fsep"></div>
    <button class="pill active" data-sort="newest">Newest</button>
    <button class="pill" data-sort="title">A–Z</button>
    <button class="pill" data-sort="foryou">✦ For You</button>
    <div class="fsep"></div>
    <button class="pill" id="swipe-open-btn">🃏 Swipe</button>
  </div>
</div>

<div class="count-bar"><span id="count-label"></span></div>
<div class="grid" id="grid"></div>
<div class="pagination" id="pagination"></div>

<!-- Swiper modal -->
<div class="swiper-overlay" id="swiper-overlay">
  <div class="swiper-header">
    <div class="swiper-header-left">
      <button class="swiper-close" id="swiper-close">✕</button>
      <span class="swiper-progress" id="swiper-progress"></span>
    </div>
    <button class="swiper-saved-btn" id="swiper-view-saved">♥ View Saved</button>
  </div>
  <div class="swiper-stack" id="swiper-stack"></div>
  <div class="swiper-actions">
    <button class="swiper-btn swiper-btn-skip" id="swiper-skip" title="Skip">✕</button>
    <button class="swiper-btn swiper-btn-save" id="swiper-save" title="Save">♥</button>
  </div>
</div>

<script>
const JOBS        = {jobs_json};
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
function scoreJob(j) {{
  let s = 10;
  const title = (j.title || '').toLowerCase();
  const team  = (j.team  || '').toLowerCase();
  const exp   = (j.experience || '').toLowerCase();

  // Role match — title
  if (/data[\\s-]?(engineer|analyst|scientist|science|pipelin)/.test(title)) s += 40;
  else if (/\\b(data|analytics|sql|\\bbi\\b|warehouse)/.test(title))          s += 22;
  if (/\\b(software[\\s-]*(engineer|developer)|swe|sde|developer|programmer)/.test(title)) s += 40;
  if (/\\b(machine[\\s-]*learning|\\bml\\b|\\bai\\b|artificial intel)/.test(title))        s += 35;
  if (/\\b(backend|frontend|full[\\s-]?stack)/.test(title))                               s += 22;
  if (/\\b(information tech|systems|infrastructure|devops|cloud|platform|\\bsre\\b)/.test(title)) s += 28;

  // Entry-level signals — generic
  if (/\\b(junior|entry[\\s-]?level|new[\\s-]*grad|early[\\s-]*career|level\\s*i\\b)/.test(title)) s += 28;
  // "associate" only boosts when paired with a tech role word
  if (/\\bassociate\\b/.test(title) && /\\b(software|engineer|developer|analyst|data|scientist|swe|sde|programmer|devops|cloud|it|security|architect)\\b/.test(title)) s += 28;
  if (/\\b(junior|entry[\\s-]?level|new[\\s-]*grad|associate)/.test(exp)) s += 35;

  // ── Company-specific level systems ──
  // Google: L3=SWE II (entry), L4=SWE III (junior-mid), L5+=Senior (penalised below)
  if (/\\b(swe\\s*(ii|2)|sde\\s*(ii|2)|software\\s*engineer\\s*(ii|2)|data\\s*engineer\\s*(ii|2))\\b/.test(title)) s += 30;
  if (/\\b(swe\\s*(iii|3)|sde\\s*(iii|3)|software\\s*engineer\\s*(iii|3))\\b/.test(title)) s += 12;
  if (/\\b(swe\\s*(iv|v|4|5|6)|software\\s*engineer\\s*(iv|v|4|5|6))\\b/.test(title)) s -= 30;
  // Meta: E3/E4 entry-junior, E5+ senior
  if (/\\bE[34]\\b/.test(title)) s += 28;
  if (/\\bE[56789]\\b/.test(title)) s -= 35;
  // Amazon: SDE I=entry (L4), SDE II=mid (L5), Senior SDE=senior (L6)
  // "sde" already +40; SDE I specifically gets extra boost
  if (/\\bsde\\s*i\\b/.test(title) && !/\\bsde\\s*ii\\b/.test(title)) s += 20;
  // Microsoft: SDE=entry, SDE II=mid, Senior SDE=senior — handled by "sde" +40 + senior penalty
  // Apple: ICT2/ICT3 entry, ICT4 mid, ICT5/6 senior
  if (/\\bict\\s*[23]\\b/.test(title)) s += 28;
  if (/\\bict\\s*4\\b/.test(title)) s += 5;
  if (/\\bict\\s*[567]\\b/.test(title)) s -= 30;
  // Stripe: IC3=entry, IC4=junior-mid, IC5+=senior
  if (/\\bic\\s*[34]\\b/.test(title)) s += 25;
  if (/\\bic\\s*[567]\\b/.test(title)) s -= 30;
  // Uber/Airbnb/Snap/Pinterest/Roblox: L3/L4=entry-mid, L5+=senior
  if (/\\b(software|swe|sde|data|ml)\\b/.test(title) && /\\bl[34]\\b/.test(title)) s += 22;
  if (/\\b(software|swe|sde|data|ml)\\b/.test(title) && /\\bl[5678]\\b/.test(title)) s -= 30;
  // Salesforce: MTS=entry, SMTS=senior, LMTS/PMTS=staff
  if (/\\bmts\\b/.test(title) && !/\\b(s|l|p)mts\\b/.test(title)) s += 20;
  if (/\\b(smts|lmts|pmts)\\b/.test(title)) s -= 25;
  // EA: Associate SE / SE I = entry
  if (/\\bse\\s*i\\b/.test(title) && !/\\bse\\s*ii\\b/.test(title)) s += 20;
  // Ubisoft: Junior Programmer handled by "junior"; Programmer=mid; Senior=penalised below
  // PNC: C1 Associate=caught by "associate"; C2 SWE neutral; C3+ Senior/Principal caught below

  // Seniority penalties
  if (/\\b(senior|sr\\.?\\s|staff\\s|principal)/.test(title)) s -= 35;
  if (/\\b(director|vp\\b|vice\\s*president|head\\s+of|chief|\\bpresident\\b)/.test(title)) s -= 50;
  if (/\\bmanager\\b/.test(title)) s -= 20;
  if (/\\b(senior|staff|principal)/.test(exp)) s -= 30;

  // Team boost
  if (/\\b(engineering|software|data|analytics|\\bml\\b|\\bai\\b|\\bit\\b|technology|infrastructure|platform|cloud|security)/.test(team)) s += 15;

  return Math.max(0, Math.min(100, s));
}}

// ── Custom multi-select dropdown factory ──
function makeDropdown(containerId, getItems, iconFn, gridMode) {{
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

const companyDrop = makeDropdown('cs-company', ()=>COMPANIES, v=>LOGOS[v], true);
const teamDrop    = makeDropdown('cs-team',    ()=>TEAMS,     null,        false);
const expDrop     = makeDropdown('cs-exp',     ()=>EXPERIENCES, null,      false);

const state = {{ q:'', newOnly:false, savedOnly:false, sort:'newest', radiusCity:'', radiusMiles:0 }};

// ── Saved jobs storage ──
function getSaved()     {{ return new Set(JSON.parse(localStorage.getItem('swipe_saved')     || '[]')); }}
function getDiscarded() {{ return new Set(JSON.parse(localStorage.getItem('swipe_discarded') || '[]')); }}
function addSaved(id)     {{ const s=[...getSaved()];     if(!s.includes(id)) s.push(id); localStorage.setItem('swipe_saved',JSON.stringify(s));     updateSavedPill(); }}
function addDiscarded(id) {{ const s=[...getDiscarded()]; if(!s.includes(id)) s.push(id); localStorage.setItem('swipe_discarded',JSON.stringify(s)); }}

function updateSavedPill() {{
  const n = getSaved().size;
  const pill = document.getElementById('pill-saved');
  const cnt  = document.getElementById('saved-count');
  pill.style.display = n > 0 ? '' : 'none';
  cnt.textContent = n;
}}

// Populate city datalist from geocoded cities
const _cityDatalist = document.getElementById('city-datalist');
Object.keys(CITY_COORDS).sort().forEach(c => {{
  const opt = document.createElement('option');
  opt.value = c;
  _cityDatalist.appendChild(opt);
}});

const HIDDEN_TITLES = /\b(retail\s+sales|sales\s+associate|cashier|store\s+(manager|associate|leader|supervisor)|sales\s+rep(resentative)?|retail\s+associate|floor\s+(associate|supervisor)|merchandise|barista|bank\s+teller|teller\b)\b/i;

function filtered() {{
  return JOBS.filter(j => {{
    if (HIDDEN_TITLES.test(j.title)) return false;
    if (state.q              && !j.title.toLowerCase().includes(state.q) && !(j.company||'').toLowerCase().includes(state.q)) return false;
    if (state.newOnly        && !j.is_new)                                 return false;
    if (state.savedOnly      && !getSaved().has(j.role_id))               return false;
    if (companyDrop.sel.size && !companyDrop.sel.has(j.company))          return false;
    if (teamDrop.sel.size    && !teamDrop.sel.has(j.team))                return false;
    if (expDrop.sel.size     && !expDrop.sel.has(j.experience))           return false;
    if (state.sort === 'foryou' && scoreJob(j) < 20)                      return false;
    if (_usOnly) {{
      const locs = getLocations(j);
      if (locs.length > 0 && !locs.some(n => n.isUS)) return false;
    }}
    if (state.radiusCity) {{
      const locs = getLocations(j);
      if (state.radiusMiles) {{
        const center = CITY_COORDS[state.radiusCity];
        if (center) {{
          const inRange = locs.some(n => {{
            const c = CITY_COORDS[n.display];
            return c && haversine(center.lat, center.lon, c.lat, c.lon) <= state.radiusMiles;
          }});
          if (!inRange) return false;
        }}
      }} else {{
        if (!locs.some(n => n.display.toLowerCase() === state.radiusCity.toLowerCase())) return false;
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
  if (rel.includes('minute'))  {{ const v=n(/(\\d+|a|an)\\s+minute/); if(v) return now - v*60*1000; }}
  if (rel.includes('hour'))    {{ const v=n(/(\\d+|a|an)\\s+hour/);   if(v) return now - v*3600*1000; }}
  if (rel.includes('day'))     {{ const v=n(/(\\d+|a|an)\\s+day/);    if(v) return now - v*86400*1000; }}
  if (rel.includes('week'))    {{ const v=n(/(\\d+|a|an)\\s+week/);   if(v) return now - v*7*86400*1000; }}
  if (rel.includes('month'))   {{ const v=n(/(\\d+|a|an)\\s+month/);  if(v) return now - v*30*86400*1000; }}
  // absolute: "Apr 19, 2026"
  const d = new Date(str);
  if (isNaN(d)) return 0;
  // future dates (e.g. expiration fields) treated as unknown
  return d.getTime() > Date.now() ? 0 : d.getTime();
}}

function sorted(arr) {{
  if (state.sort === 'title')  return [...arr].sort((a,b)=>a.title.localeCompare(b.title));
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

  grid.innerHTML = '';
  if (!page.length) {{
    grid.innerHTML = '<div class="no-results">No jobs match your filters.</div>';
    renderPagination(0, 0);
    return;
  }}
  const frag = document.createDocumentFragment();
  page.forEach(j => {{
    const logoSrc = LOGOS[j.company];
    const sc = state.sort === 'foryou' ? scoreJob(j) : -1;
    const matchColor = sc >= 70 ? '#34c759' : sc >= 40 ? '#ff9500' : '#8e8e93';
    const isSaved = getSaved().has(j.role_id);
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
      <div class="card-top">
        ${{logoSrc ? `<img class="logo" src="${{logoSrc}}" alt="${{j.company}}"/>` : ''}}
        <span class="company-label">${{j.company}}</span>
        <div class="card-top-right">
          ${{j.is_new ? '<span class="new-badge">NEW</span>' : ''}}
          ${{sc >= 0 ? `<span class="match-badge" style="background:${{matchColor}}">${{sc}}%</span>` : ''}}
          <button class="card-save-btn${{isSaved ? ' saved' : ''}}" title="${{isSaved ? 'Unsave' : 'Save'}}">♥</button>
        </div>
      </div>
      <div class="card-title"><a href="${{j.url}}" target="_blank" rel="noopener">${{j.title}}</a></div>
      <div class="tags">
        ${{j.team       ? `<span class="tag tag-team">${{j.team}}</span>` : ''}}
        ${{j.experience ? `<span class="tag tag-exp">${{j.experience}}</span>` : ''}}
        ${{j.location   ? `<span class="tag tag-loc">📍 ${{j.location}}</span>` : ''}}
      </div>
      <div class="card-date">
        ${{j.posted_date ? `Posted ${{j.posted_date}}` : `First seen ${{j.first_seen}}`}}
      </div>
    `;
    card.querySelector('.card-save-btn').addEventListener('click', e => {{
      e.stopPropagation();
      const saved = getSaved();
      const btn = e.currentTarget;
      if (saved.has(j.role_id)) {{
        const arr = [...saved].filter(id => id !== j.role_id);
        localStorage.setItem('swipe_saved', JSON.stringify(arr));
        btn.classList.remove('saved');
        btn.title = 'Save';
      }} else {{
        addSaved(j.role_id);
        btn.classList.add('saved');
        btn.title = 'Unsave';
      }}
      updateSavedPill();
      if (state.savedOnly) render();
    }});
    frag.appendChild(card);
  }});
  grid.appendChild(frag);
  renderPagination(list.length, totalPages);
}}

function render() {{
  currentPage = 1;
  renderPage(sorted(filtered()));
}}

document.getElementById('q').addEventListener('input', e => {{ state.q = e.target.value.trim().toLowerCase(); render(); }});
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
  b.classList.add('active'); state.sort = b.dataset.sort; render();
}}));

const _radiusCityEl  = document.getElementById('radius-city');
const _radiusMilesEl = document.getElementById('radius-miles');
const _radiusClearEl = document.getElementById('radius-clear');
_radiusCityEl.addEventListener('input', () => {{
  state.radiusCity = _radiusCityEl.value.trim();
  _radiusCityEl.classList.toggle('active', !!state.radiusCity);
  _radiusClearEl.style.display = state.radiusCity ? '' : 'none';
  render();
}});
_radiusClearEl.addEventListener('click', () => {{
  _radiusCityEl.value = '';
  state.radiusCity = '';
  _radiusCityEl.classList.remove('active');
  _radiusClearEl.style.display = 'none';
  render();
}});
_radiusMilesEl.addEventListener('change', () => {{
  state.radiusMiles = parseInt(_radiusMilesEl.value) || 0;
  _radiusMilesEl.classList.toggle('active', !!state.radiusMiles);
  render();
}});

updateSavedPill();

// ── "Saved" pill in filter strip ──
document.getElementById('pill-saved').addEventListener('click', function() {{
  document.querySelectorAll('[data-new]').forEach(x=>x.classList.remove('active'));
  const wasActive = state.savedOnly;
  state.savedOnly = !wasActive;
  if (state.savedOnly) this.classList.add('active');
  else {{ state.newOnly = false; document.querySelector('[data-new="all"]').classList.add('active'); }}
  render();
}});

// ── Swiper ──
let swipeQueue = [];
let swipeIdx   = 0;
let dragState  = null;

function isUSJob(j) {{
  const locs = getLocations(j);
  if (locs.length === 0) return true;
  return locs.some(n => n.isUS);
}}

function buildSwipeQueue() {{
  const seen = new Set([...getSaved(), ...getDiscarded()]);
  const candidates = JOBS.filter(j =>
    !HIDDEN_TITLES.test(j.title) && !seen.has(j.role_id) && scoreJob(j) >= 20 && isUSJob(j)
  );
  return candidates.sort((a,b) => {{
    if (a.is_new !== b.is_new) return a.is_new ? -1 : 1;
    return scoreJob(b) - scoreJob(a) || a.title.localeCompare(b.title);
  }});
}}

function renderSwiperCard(j) {{
  if (!j) return '';
  const sc        = scoreJob(j);
  const logoSrc   = LOGOS[j.company];
  const pctColor  = sc >= 70 ? '#34c759' : sc >= 40 ? '#ff9500' : '#8e8e93';
  const logoHTML  = logoSrc
    ? `<img class="swiper-logo" src="${{logoSrc}}" alt="${{j.company}}"/>`
    : `<div class="swiper-logo-placeholder">${{(j.company||'?')[0]}}</div>`;
  return `
    <div class="swipe-indicator swipe-save-ind" id="sw-save-ind">♥ SAVE</div>
    <div class="swipe-indicator swipe-skip-ind" id="sw-skip-ind">✕ SKIP</div>
    <div class="swiper-logo-wrap">
      ${{logoHTML}}
      <span class="swiper-company">${{j.company}}</span>
    </div>
    <div class="swiper-title">${{j.title}}</div>
    <div class="swiper-meta">
      ${{j.location   ? `<div class="swiper-meta-row"><span class="swiper-meta-icon">📍</span><span>${{j.location}}</span></div>` : ''}}
      ${{j.team       ? `<div class="swiper-meta-row"><span class="swiper-meta-icon">🏢</span><span>${{j.team}}</span></div>` : ''}}
      ${{j.experience ? `<div class="swiper-meta-row"><span class="swiper-meta-icon">🎓</span><span>${{j.experience}}</span></div>` : ''}}
      ${{(j.posted_date||j.first_seen) ? `<div class="swiper-meta-row"><span class="swiper-meta-icon">📅</span><span>${{j.posted_date ? 'Posted '+j.posted_date : 'First seen '+j.first_seen}}</span></div>` : ''}}
    </div>
    <div class="swiper-badges">
      ${{j.is_new ? '<span class="swiper-badge-new">NEW</span>' : ''}}
      <span class="swiper-badge-pct" style="background:${{pctColor}}">${{sc}}% match</span>
    </div>
  `;
}}

function renderSwipeStack() {{
  const stack = document.getElementById('swiper-stack');
  const prog  = document.getElementById('swiper-progress');
  const remaining = swipeQueue.length - swipeIdx;
  stack.innerHTML = '';

  if (remaining <= 0) {{
    document.querySelector('.swiper-actions').style.display = 'none';
    stack.innerHTML = `<div class="swiper-done">
      <div class="swiper-done-title">All caught up! 🎉</div>
      <div>Come back after the next scrape for fresh jobs.</div>
    </div>`;
    prog.textContent = '';
    return;
  }}
  document.querySelector('.swiper-actions').style.display = '';
  prog.textContent = `${{remaining}} left`;

  if (remaining >= 3) {{
    const back2 = document.createElement('div');
    back2.className = 'swiper-card-back2';
    stack.appendChild(back2);
  }}
  if (remaining >= 2) {{
    const back1 = document.createElement('div');
    back1.className = 'swiper-card-back';
    stack.appendChild(back1);
  }}

  const card = document.createElement('div');
  card.className = 'swiper-card';
  card.innerHTML = renderSwiperCard(swipeQueue[swipeIdx]);
  stack.appendChild(card);
  attachDrag(card);
}}

function doSwipe(dir) {{  // dir: 'save' | 'skip'
  const card = document.querySelector('.swiper-card');
  if (!card) return;
  const j = swipeQueue[swipeIdx];
  if (dir === 'save') {{ addSaved(j.role_id); card.classList.add('swipe-left'); }}
  else                {{ addDiscarded(j.role_id); card.classList.add('swipe-right'); }}
  card.style.transform = dir === 'save'
    ? 'translateX(-120%) rotate(-18deg)'
    : 'translateX(120%) rotate(18deg)';
  card.style.opacity = '0';
  swipeIdx++;
  setTimeout(renderSwipeStack, 320);
}}

function attachDrag(card) {{
  let startX=0, startY=0, dx=0, didDrag=false;
  const j = swipeQueue[swipeIdx];

  function onStart(e) {{
    const pt = e.touches ? e.touches[0] : e;
    startX = pt.clientX; startY = pt.clientY; dx = 0; didDrag = false;
    dragState = true;
    card.style.transition = 'none';
  }}
  function onMove(e) {{
    if (!dragState) return;
    const pt = e.touches ? e.touches[0] : e;
    dx = pt.clientX - startX;
    if (Math.abs(dx) > 8) didDrag = true;
    const rot = dx * 0.08;
    card.style.transform = `translateX(${{dx}}px) rotate(${{rot}}deg)`;
    const t = Math.min(Math.abs(dx) / 80, 1);
    const saveInd = document.getElementById('sw-save-ind');
    const skipInd = document.getElementById('sw-skip-ind');
    if (dx < 0) {{
      if(saveInd) saveInd.style.opacity = t;
      if(skipInd) skipInd.style.opacity = 0;
    }} else {{
      if(skipInd) skipInd.style.opacity = t;
      if(saveInd) saveInd.style.opacity = 0;
    }}
    if (e.cancelable) e.preventDefault();
  }}
  function onEnd() {{
    if (!dragState) return;
    dragState = false;
    card.style.transition = '';
    const saveInd = document.getElementById('sw-save-ind');
    const skipInd = document.getElementById('sw-skip-ind');
    if (Math.abs(dx) > 90) {{
      doSwipe(dx < 0 ? 'save' : 'skip');
    }} else {{
      card.style.transform = '';
      if(saveInd) saveInd.style.opacity = 0;
      if(skipInd) skipInd.style.opacity = 0;
      if (!didDrag && j && j.url) window.open(j.url, '_blank', 'noopener');
    }}
  }}

  card.addEventListener('mousedown',  onStart);
  card.addEventListener('touchstart', onStart, {{ passive: false }});
  window.addEventListener('mousemove',  onMove);
  window.addEventListener('touchmove',  onMove, {{ passive: false }});
  window.addEventListener('mouseup',    onEnd, {{ once: true }});
  window.addEventListener('touchend',   onEnd, {{ once: true }});
}}

function openSwiper() {{
  swipeQueue = buildSwipeQueue();
  swipeIdx   = 0;
  document.getElementById('swiper-overlay').classList.add('open');
  document.querySelector('.swiper-actions').style.display = '';
  renderSwipeStack();
}}

document.getElementById('swipe-open-btn').addEventListener('click', openSwiper);
document.getElementById('swiper-close').addEventListener('click', () => {{
  document.getElementById('swiper-overlay').classList.remove('open');
  render();
}});
document.getElementById('swiper-skip').addEventListener('click', () => doSwipe('skip'));
document.getElementById('swiper-save').addEventListener('click', () => doSwipe('save'));
document.getElementById('swiper-view-saved').addEventListener('click', () => {{
  document.getElementById('swiper-overlay').classList.remove('open');
  state.savedOnly = true;
  state.newOnly   = false;
  document.querySelectorAll('[data-new]').forEach(x=>x.classList.remove('active'));
  document.getElementById('pill-saved').classList.add('active');
  render();
}});
document.addEventListener('keydown', e => {{
  if (!document.getElementById('swiper-overlay').classList.contains('open')) return;
  if (e.key === 'ArrowLeft')  doSwipe('save');
  if (e.key === 'ArrowRight') doSwipe('skip');
  if (e.key === 'Escape')     document.getElementById('swiper-overlay').classList.remove('open');
}});

render();
</script>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"Built index.html — {len(jobs)} jobs, {new_count} new")
webbrowser.open("index.html")

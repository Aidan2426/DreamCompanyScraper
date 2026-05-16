import asyncio
import argparse
import json
from datetime import date

from db import init_db, upsert_jobs, get_new_jobs, get_all_jobs
from scrapers import apple, google, microsoft, netflix, meta, amazon, openai, anthropic, disney, nvidia, hershey, ibm, cisco, oracle, universal, duolingo, hp, intel, qualcomm, micron, paramount, adobe, motorola, samsung, analogdevices, ebay, gecko, westerndigital, nps, xai, palantir, sony, nintendo, ea, epicgames, roblox, ubisoft, pinterest, linkedin, supercell, pwc, spotify, verizon, amd, salesforce, uber, airbnb, dropbox, twitch, yahoo, riotgames, fujifilm, pnc, upmc, natgeo, panasonic, snap, logitech, cloudflare, peloton, zillow, garmin, autodesk, deloitte, wesco, viatris, dsg, alcoa, arconic, westinghouse, eqt, howmet, americaneagle, coherent, nike, adidas, razer, stripe, notion, workatastartup, visa, bny, mastercard, generaldynamics, ford, sandisk, figma, capitalone, crowdstrike, boeing, wabtec, lenovo, tesla, spacex, lockheed, paypal, dell, broadcom, robopgh, aqua, cmu, covestro, fnb, bechtel, highmark, kennametal, leidos, servicenow, united, armada, bytedance, wbd, seatgeek, ticketmaster, stubhub, cgi, indeed, affirm, formenergy, gevernova, bdo, emerson, questdiagnostics, ey, fedex, gianteagle, atimaterials, ppg, gm

TODAY = date.today().isoformat()


async def run_one(name, scraper):
    try:
        if asyncio.iscoroutinefunction(scraper.scrape):
            jobs = await scraper.scrape()
        else:
            jobs = await asyncio.get_event_loop().run_in_executor(None, scraper.scrape)
        print(f"[OK] {name.title()}: {len(jobs)} jobs")
        return jobs
    except Exception as e:
        print(f"[FAIL] {name.title()} failed: {e}")
        return []


async def run(skip_scrape: bool = False, companies: list = None, skip: list = None):
    init_db()

    if not skip_scrape:
        all_scrapers = {"apple": apple, "google": google, "microsoft": microsoft, "netflix": netflix, "meta": meta, "amazon": amazon, "openai": openai, "anthropic": anthropic, "disney": disney, "nvidia": nvidia, "hershey": hershey, "ibm": ibm, "cisco": cisco, "oracle": oracle, "universal": universal, "duolingo": duolingo, "hp": hp, "intel": intel, "qualcomm": qualcomm, "micron": micron, "paramount": paramount, "adobe": adobe, "motorola": motorola, "samsung": samsung, "analogdevices": analogdevices, "ebay": ebay, "gecko": gecko, "westerndigital": westerndigital, "nps": nps, "xai": xai, "palantir": palantir, "sony": sony, "nintendo": nintendo, "ea": ea, "epicgames": epicgames, "roblox": roblox, "ubisoft": ubisoft, "pinterest": pinterest, "linkedin": linkedin, "supercell": supercell, "pwc": pwc, "spotify": spotify, "verizon": verizon, "amd": amd, "salesforce": salesforce, "uber": uber, "airbnb": airbnb, "dropbox": dropbox, "twitch": twitch, "yahoo": yahoo, "riotgames": riotgames, "fujifilm": fujifilm, "pnc": pnc, "upmc": upmc, "natgeo": natgeo, "panasonic": panasonic, "snap": snap, "logitech": logitech, "cloudflare": cloudflare, "peloton": peloton, "zillow": zillow, "garmin": garmin, "autodesk": autodesk, "deloitte": deloitte, "wesco": wesco, "viatris": viatris, "dsg": dsg, "alcoa": alcoa, "arconic": arconic, "westinghouse": westinghouse, "eqt": eqt, "howmet": howmet, "americaneagle": americaneagle, "coherent": coherent, "nike": nike, "adidas": adidas, "razer": razer, "stripe": stripe, "notion": notion, "workatastartup": workatastartup, "visa": visa, "bny": bny, "mastercard": mastercard, "generaldynamics": generaldynamics, "ford": ford, "sandisk": sandisk, "figma": figma, "capitalone": capitalone, "crowdstrike": crowdstrike, "boeing": boeing, "wabtec": wabtec, "lenovo": lenovo, "tesla": tesla, "spacex": spacex, "lockheed": lockheed, "paypal": paypal, "dell": dell, "broadcom": broadcom, "robopgh": robopgh, "aqua": aqua, "cmu": cmu, "covestro": covestro, "fnb": fnb, "bechtel": bechtel, "highmark": highmark, "kennametal": kennametal, "leidos": leidos, "servicenow": servicenow, "united": united, "armada": armada, "bytedance": bytedance, "wbd": wbd, "seatgeek": seatgeek, "ticketmaster": ticketmaster, "stubhub": stubhub, "cgi": cgi, "indeed": indeed, "affirm": affirm, "formenergy": formenergy, "gevernova": gevernova, "bdo": bdo, "emerson": emerson, "questdiagnostics": questdiagnostics, "ey": ey, "fedex": fedex, "gianteagle": gianteagle, "atimaterials": atimaterials, "ppg": ppg, "gm": gm}
        ALWAYS_SKIP = {"linkedin"}
        run_scrapers = {k: v for k, v in all_scrapers.items()
                        if (not companies or k in companies) and k not in ALWAYS_SKIP and (not skip or k not in skip)}

        print(f"Running {len(run_scrapers)} scrapers in parallel...\n")
        results = await asyncio.gather(*[run_one(name, scraper) for name, scraper in run_scrapers.items()])
        all_scraped = [job for batch in results for job in batch]

        if not all_scraped:
            print("No jobs scraped.")
            return

        new_count = upsert_jobs(all_scraped)
        print(f"\n[OK] {len(all_scraped)} total scraped, {new_count} new today\n")

    # Dump all jobs to jobs.json for build.py
    all_jobs = get_all_jobs()
    today = TODAY
    jobs_export = [
        {
            "role_id":     j["role_id"],
            "title":       j["title"],
            "team":        j["team"],
            "location":    j["location"],
            "posted_date": j["posted_date"],
            "url":         j["url"],
            "company":     j["company"],
            "first_seen":  j["first_seen"],
            "is_new":      j["first_seen"] == today,
            "experience":  j["experience"] or "",
        }
        for j in all_jobs
    ]
    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump({"scraped_at": today, "jobs": jobs_export}, f, ensure_ascii=False)
    print(f"Wrote jobs.json ({len(jobs_export)} jobs)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dream Company Job Scraper")
    parser.add_argument("--skip-scrape", action="store_true", help="Skip scraping, just rebuild jobs.json from DB")
    parser.add_argument("--company", nargs="+", help="Only run specific scrapers e.g. --company apple google")
    parser.add_argument("--skip", nargs="+", help="Skip specific scrapers e.g. --skip apple google meta")
    args = parser.parse_args()

    companies = [c.lower() for c in args.company] if args.company else None
    skip = [c.lower() for c in args.skip] if args.skip else None
    asyncio.run(run(skip_scrape=args.skip_scrape, companies=companies, skip=skip))

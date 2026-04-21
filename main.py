import asyncio
import argparse
import json
from datetime import date

from db import init_db, upsert_jobs, get_new_jobs, get_all_jobs
from scrapers import apple, google, microsoft, netflix, meta, amazon, openai, anthropic, disney, nvidia, hershey, ibm, cisco, oracle, universal, duolingo, hp, intel, qualcomm, micron, paramount, adobe, motorola, samsung, analogdevices, ebay, gecko, westerndigital, nps, xai, palantir, sony, nintendo, ea

TODAY = date.today().isoformat()


async def run(skip_scrape: bool = False, companies: list = None):
    init_db()

    if not skip_scrape:
        all_scrapers = {"apple": apple, "google": google, "microsoft": microsoft, "netflix": netflix, "meta": meta, "amazon": amazon, "openai": openai, "anthropic": anthropic, "disney": disney, "nvidia": nvidia, "hershey": hershey, "ibm": ibm, "cisco": cisco, "oracle": oracle, "universal": universal, "duolingo": duolingo, "hp": hp, "intel": intel, "qualcomm": qualcomm, "micron": micron, "paramount": paramount, "adobe": adobe, "motorola": motorola, "samsung": samsung, "analogdevices": analogdevices, "ebay": ebay, "gecko": gecko, "westerndigital": westerndigital, "nps": nps, "xai": xai, "palantir": palantir, "sony": sony, "nintendo": nintendo, "ea": ea}
        run_scrapers = {k: v for k, v in all_scrapers.items() if not companies or k in companies}

        all_scraped = []
        for name, scraper in run_scrapers.items():
            print(f"\n{'='*50}\nRunning {name.title()} scraper...\n{'='*50}")
            try:
                # Support both async and sync scrapers
                if asyncio.iscoroutinefunction(scraper.scrape):
                    jobs = await scraper.scrape()
                else:
                    jobs = await asyncio.get_event_loop().run_in_executor(None, scraper.scrape)
                all_scraped.extend(jobs)
                print(f"[OK] {name.title()}: {len(jobs)} jobs")
            except Exception as e:
                print(f"[FAIL] {name.title()} failed: {e}")

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
    args = parser.parse_args()

    companies = [c.lower() for c in args.company] if args.company else None
    asyncio.run(run(skip_scrape=args.skip_scrape, companies=companies))

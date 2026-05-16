import httpx
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Referer": "https://careers.cisco.com/global/en/search-results",
}

BASE_BODY = {
    "sortBy": "",
    "subsearch": "",
    "jobs": True,
    "counts": True,
    "all_fields": ["category", "raasJobRequisitionType", "country", "state", "city", "type", "RemoteType"],
    "pageName": "search-results",
    "size": 10,
    "clearAll": False,
    "jdsource": "facets",
    "isSliderEnable": False,
    "pageId": "page4",
    "siteType": "external",
    "keywords": "",
    "global": True,
    "selected_fields": {},
    "lang": "en_global",
    "deviceType": "desktop",
    "country": "global",
    "refNum": "CISCISGLOBAL",
}

with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
    for ddoKey in ["eagerLoadRefineSearch", "eagerLoadRefineSearchSession", "refineSearch"]:
        for from_val in [0, 10]:
            body = {**BASE_BODY, "from": from_val, "ddoKey": ddoKey}
            r = client.post("https://careers.cisco.com/widgets", json=body)
            data = r.json()
            print(f"ddoKey={ddoKey} from={from_val}: status={r.status_code}")

            # Check result structure
            if ddoKey in data:
                inner = data[ddoKey]
                total = inner.get("totalHits")
                jobs = inner.get("data", {}).get("jobs", []) if isinstance(inner.get("data"), dict) else []
                print(f"  totalHits={total}, jobs={len(jobs)}")
                if jobs:
                    print(f"  first: {jobs[0].get('title')} | {jobs[0].get('reqId')}")
            else:
                print(f"  keys: {list(data.keys())}")
                print(f"  preview: {str(data)[:200]}")
            print()

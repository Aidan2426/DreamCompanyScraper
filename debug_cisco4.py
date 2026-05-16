from playwright.sync_api import sync_playwright
import json

search_requests = []
search_responses = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    def on_request(request):
        if "careers.cisco.com/widgets" in request.url and request.post_data:
            body = request.post_data
            if "refineSearch" in body or "sortBy" in body:
                search_requests.append(body)

    def on_response(response):
        if "careers.cisco.com/widgets" in response.url:
            ct = response.headers.get("content-type", "")
            if "json" in ct:
                try:
                    body = response.body().decode("utf-8", "replace")
                    if "refineSearch" in body and "jobs" in body:
                        search_responses.append(body)
                except:
                    pass

    page.on("request", on_request)
    page.on("response", on_response)

    print("Loading page 1...")
    page.goto("https://careers.cisco.com/global/en/search-results", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)

    print("Loading page 2 (?s=1)...")
    page.goto("https://careers.cisco.com/global/en/search-results?s=1", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)

    browser.close()

print(f"\n=== Search Requests ({len(search_requests)}) ===")
for i, req in enumerate(search_requests):
    print(f"\n--- Request {i+1} ---")
    try:
        print(json.dumps(json.loads(req), indent=2))
    except:
        print(req)

print(f"\n=== Search Responses ({len(search_responses)}) ===")
for i, resp in enumerate(search_responses[:2]):
    print(f"\n--- Response {i+1} (first 1500 chars) ---")
    try:
        data = json.loads(resp)
        rs = data.get("refineSearch", {})
        print("totalHits:", rs.get("totalHits"))
        print("hits:", rs.get("hits"))
        jobs = rs.get("data", {}).get("jobs", [])
        print("jobs count:", len(jobs))
        if jobs:
            j = jobs[0]
            print("first job:", {k: j.get(k) for k in ["title", "location", "postedDate", "reqId", "applyUrl", "category"]})
    except Exception as e:
        print(f"Parse error: {e}")
        print(resp[:500])

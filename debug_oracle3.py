from playwright.sync_api import sync_playwright
import json

req_urls = []
resp_data = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    def on_request(request):
        url = request.url
        if "recruitingCEJobRequisitions" in url:
            req_urls.append(url)

    def on_response(response):
        url = response.url
        if "recruitingCEJobRequisitions" in url:
            try:
                body = response.body().decode("utf-8", "replace")
                resp_data.append({"url": url, "body": body})
            except:
                pass

    page.on("request", on_request)
    page.on("response", on_response)

    print("Loading Oracle careers...")
    page.goto("https://careers.oracle.com/en/sites/jobsearch/jobs?mode=location", wait_until="networkidle", timeout=45000)
    page.wait_for_timeout(3000)

    # Click show more
    try:
        btn = page.get_by_role("button", name=re.compile("show more|see more|load more", re.IGNORECASE)).first if False else None
        # Try different selectors
        for sel in ["button[data-qa='showMore']", ".show-more", "[data-testid='show-more']", "button:has-text('More')", "button:has-text('more')"]:
            try:
                el = page.locator(sel).first
                if el.is_visible(timeout=2000):
                    el.click()
                    page.wait_for_timeout(3000)
                    print(f"Clicked: {sel}")
                    break
            except:
                pass
    except Exception as e:
        print(f"Show more: {e}")

    browser.close()

import re
print(f"\n=== Job Requisitions URLs ({len(req_urls)}) ===")
for u in req_urls:
    print(u)
    print()

print(f"\n=== First Response ===")
if resp_data:
    try:
        data = json.loads(resp_data[0]["body"])
        items = data.get("items", [])
        if items:
            item = items[0]
            print("Top-level keys:", list(item.keys())[:20])
            # Find the job list
            req_list = item.get("requisitionList", [])
            print(f"Jobs in page: {len(req_list)}")
            print(f"TotalJobsCount: {item.get('TotalJobsCount')}")
            if req_list:
                j = req_list[0]
                print("Job keys:", list(j.keys()))
                print("First job:", {k: j.get(k) for k in ["Id", "Title", "PostedDate", "PrimaryLocation", "PrimaryLocationCode", "ExternalDescriptionId"]})
    except Exception as e:
        print(f"Parse error: {e}")
        print(resp_data[0]["body"][:1000])

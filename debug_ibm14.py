"""
Use Playwright to capture actual network requests from IBM careers search.
"""
from playwright.sync_api import sync_playwright

api_calls = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    def on_request(request):
        url = request.url
        if any(k in url for k in ["search", "/api/", "job", "career", "requisition"]) and not any(x in url for x in ["google", "adobe", "akamai", "cdn", "analytics", "telemetry"]):
            api_calls.append(f"REQ {request.method} {url}")

    def on_response(response):
        url = response.url
        ct = response.headers.get("content-type", "")
        if "json" in ct and any(k in url for k in ["search", "/api/", "job", "career", "requisition"]):
            try:
                body = response.body()
                api_calls.append(f"RESP {url}\n  body: {body[:400].decode('utf-8','replace')}")
            except:
                api_calls.append(f"RESP {url} (body read failed)")

    page.on("request", on_request)
    page.on("response", on_response)

    print("Loading IBM careers search page...")
    try:
        page.goto("https://www.ibm.com/careers/search?sort=dcdate_desc", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(8000)
    except Exception as e:
        print(f"Navigation note: {e}")

    browser.close()

print(f"\nCaptured {len(api_calls)} relevant calls:")
for call in api_calls:
    print(call[:300])
    print()

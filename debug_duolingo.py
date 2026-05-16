from playwright.sync_api import sync_playwright
import json

captured = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    def on_request(request):
        url = request.url
        if not any(x in url for x in ["google", "analytics", "doubleclick", "linkedin", "bing", "cdn", ".css", ".png", ".svg", ".woff", "fonts", "gtm", "clarity"]):
            if any(k in url.lower() for k in ["job", "career", "api", "lever", "greenhouse", "workday", "ashby", "position", "opening"]):
                captured.append({"type": "REQ", "method": request.method, "url": url, "body": request.post_data})

    def on_response(response):
        url = response.url
        ct = response.headers.get("content-type", "")
        if "json" in ct and not any(x in url for x in ["google", "analytics", "gtm"]):
            if any(k in url.lower() for k in ["job", "career", "api", "lever", "greenhouse", "workday", "ashby", "position", "opening"]):
                try:
                    body = response.body()
                    captured.append({"type": "RESP", "url": url, "body": body[:800].decode("utf-8", "replace")})
                except:
                    pass

    page.on("request", on_request)
    page.on("response", on_response)

    print("Loading Duolingo careers...")
    page.goto("https://careers.duolingo.com/#careers", wait_until="networkidle", timeout=45000)
    page.wait_for_timeout(3000)
    print("Final URL:", page.url)

    browser.close()

print(f"\nCaptured {len(captured)} events:")
for c in captured:
    if c["type"] == "REQ":
        print(f"REQ {c['method']} {c['url'][:150]}")
        if c.get("body"):
            print(f"  body: {c['body'][:200]}")
    else:
        print(f"RESP {c['url'][:120]}")
        print(f"  {c['body'][:400]}")
    print()

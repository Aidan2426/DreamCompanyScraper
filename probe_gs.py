import asyncio, json, re
from curl_cffi.requests import AsyncSession

async def probe():
    async with AsyncSession(impersonate="chrome124") as s:
        await s.get("https://higher.gs.com/results?page=1&sort=POSTED_DATE", timeout=20)

        rjs = await s.get("https://higher.gs.com/_next/static/chunks/pages/_app-b30eefd44abc7adb.js", timeout=20)
        js = rjs.text

        ENDPOINT = "https://api-higher.gs.com/gateway/api/v1/graphql"
        GQL_HEADERS = {
            "Content-Type": "application/json",
            "Origin": "https://higher.gs.com",
            "Referer": "https://higher.gs.com/",
        }

        QUERY = """
  query GetRoles($searchQueryInput: RoleSearchQueryInput!) {
    roleSearch(searchQueryInput: $searchQueryInput) {
      totalCount
      items {
        roleId
        corporateTitle
        jobTitle
        jobFunction
        locations {
          primary
          state
          country
          city
        }
        status
        division
        skills
        jobType {
          code
          description
        }
        externalSource {
          sourceId
        }
      }
    }
  }
"""

        import json as _json
        import urllib.request as _urllib

        def _post(payload_dict):
            body = _json.dumps(payload_dict).encode("utf-8")
            req = _urllib.Request(ENDPOINT, data=body, headers={
                "Content-Type": "application/json",
                "Origin": "https://higher.gs.com",
                "Referer": "https://higher.gs.com/",
                "User-Agent": "Mozilla/5.0",
            }, method="POST")
            with _urllib.urlopen(req, timeout=20) as r:
                return _json.loads(r.read().decode("utf-8"))

        # 1. Introspect RoleSearchQueryInput
        intro = _post({"query": """
            { __type(name: "RoleSearchQueryInput") {
                kind name
                inputFields { name type { name kind ofType { name kind } } }
            }}"""})
        print("RoleSearchQueryInput:", _json.dumps(intro, indent=2))

        # 2. Try: send variables as a JSON string (legacy Apollo pattern)
        print("\n--- Try variables as JSON string ---")
        try:
            r2 = _post({
                "operationName": "GetRoles",
                "query": QUERY,
                "variables": _json.dumps({"searchQueryInput": {
                    "page": {"pageSize": 20, "pageNumber": 0},
                    "sort": "POSTED_DATE",
                    "filters": [],
                    "experiences": ["EARLY_CAREER", "PROFESSIONAL"],
                    "searchTerm": ""
                }})
            })
            if "errors" in r2:
                print("ERRORS:", r2["errors"][0]["message"])
            else:
                rs = r2["data"]["roleSearch"]
                print(f"totalCount={rs['totalCount']} items={len(rs['items'])}")
        except Exception as e:
            print(f"Error: {e}")

asyncio.run(probe())

import httpx

API_URL = "https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobBoardWithTeams"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Origin": "https://jobs.ashbyhq.com",
    "Referer": "https://jobs.ashbyhq.com/openai",
}

QUERY = """
query ApiJobBoardWithTeams($organizationHostedJobsPageName: String!) {
  jobBoard: jobBoardWithTeams(
    organizationHostedJobsPageName: $organizationHostedJobsPageName
  ) {
    teams { id name externalName parentTeamId }
    jobPostings {
      id
      title
      teamId
      locationId
      locationName
      workplaceType
      employmentType
      secondaryLocations { ...JobPostingSecondaryLocationParts }
      compensationTierSummary
    }
  }
}

fragment JobPostingSecondaryLocationParts on JobPostingSecondaryLocation {
  locationId
  locationName
}
"""


def scrape() -> list[dict]:
    payload = {
        "operationName": "ApiJobBoardWithTeams",
        "variables": {"organizationHostedJobsPageName": "openai"},
        "query": QUERY,
    }

    with httpx.Client(timeout=30, headers=HEADERS) as client:
        r = client.post(API_URL, json=payload)
        r.raise_for_status()
        data = r.json()

    # Debug: print top-level keys to find correct field name
    board = (data.get("data") or {}).get("jobBoard") or {}
    print(f"[openai] Board keys: {list(board.keys())}")

    teams_raw = board.get("teams", [])
    postings = board.get("jobPostings", [])

    # Build team id → name map
    team_map = {t["id"]: t["name"] for t in teams_raw}

    print(f"[openai] {len(postings)} job postings found")

    all_jobs = []
    for j in postings:
        role_id  = str(j.get("id") or "")
        title    = (j.get("title") or "").strip()
        team_id  = j.get("teamId") or ""
        team     = team_map.get(team_id, "")
        location = (j.get("locationName") or "").strip()
        workplace = (j.get("workplaceType") or "").lower()
        if workplace == "remote":
            location = (location + " (Remote)").strip() if location else "Remote"
        url = f"https://jobs.ashbyhq.com/openai/{role_id}"

        if role_id and title:
            all_jobs.append({
                "role_id":     role_id,
                "title":       title,
                "team":        team,
                "location":    location,
                "posted_date": "",
                "url":         url,
                "company":     "OpenAI",
            })

    print(f"[openai] Done. {len(all_jobs)} jobs.")
    return all_jobs


if __name__ == "__main__":
    jobs = scrape()
    for j in jobs[:5]:
        print(j)

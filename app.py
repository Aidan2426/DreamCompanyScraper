from flask import Flask, render_template, request, send_file
from db import init_db, get_all_jobs, get_new_jobs
from datetime import date
from pathlib import Path

app = Flask(__name__)
init_db()

COMPANY_LOGOS = {
    "Apple": "https://www.apple.com/ac/globalnav/7/en_US/images/be15095f-5a20-57d0-ad14-cf4c638e223a/globalnav_apple_image__b5er5ngrzxqq_large.svg",
}

PER_PAGE = 30

@app.route("/")
def index():
    root = Path(__file__).resolve().parent
    index_path = root / "index.html"

    if index_path.exists():
        return send_file(index_path, mimetype="text/html")

    since = request.args.get("since", "")
    search = request.args.get("q", "").strip().lower()
    team = request.args.get("team", "").strip()
    page = max(1, int(request.args.get("page", 1)))

    jobs = get_new_jobs(since) if since else get_all_jobs()

    if search:
        jobs = [j for j in jobs if search in j["title"].lower() or search in (j["team"] or "").lower() or search in j["company"].lower()]
    if team:
        jobs = [j for j in jobs if (j["team"] or "") == team]

    total = len(jobs)
    total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
    page = min(page, total_pages)
    jobs = jobs[(page - 1) * PER_PAGE : page * PER_PAGE]

    all_jobs_for_teams = get_all_jobs()
    teams = sorted(set(j["team"] for j in all_jobs_for_teams if j["team"]))

    return render_template("index.html",
        jobs=jobs,
        teams=teams,
        since=since,
        search=search,
        selected_team=team,
        today=date.today().isoformat(),
        logos=COMPANY_LOGOS,
        page=page,
        total_pages=total_pages,
        total=total,
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)

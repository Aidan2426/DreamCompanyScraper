from flask import Flask, render_template, request
from db import init_db, get_all_jobs, get_new_jobs
from datetime import date

app = Flask(__name__)
init_db()

COMPANY_LOGOS = {
    "Apple": "https://www.apple.com/ac/globalnav/7/en_US/images/be15095f-5a20-57d0-ad14-cf4c638e223a/globalnav_apple_image__b5er5ngrzxqq_large.svg",
}

@app.route("/")
def index():
    since = request.args.get("since", "")
    search = request.args.get("q", "").strip().lower()
    team = request.args.get("team", "").strip()

    jobs = get_new_jobs(since) if since else get_all_jobs()

    if search:
        jobs = [j for j in jobs if search in j["title"].lower() or search in (j["team"] or "").lower()]
    if team:
        jobs = [j for j in jobs if (j["team"] or "") == team]

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
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)

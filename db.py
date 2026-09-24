import sqlite3
from datetime import date
from pathlib import Path

DB_PATH = Path(__file__).parent / "jobs.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                role_id       TEXT PRIMARY KEY,
                title         TEXT NOT NULL,
                team          TEXT,
                location      TEXT,
                posted_date   TEXT,
                url           TEXT,
                company       TEXT NOT NULL DEFAULT 'Apple',
                first_seen    TEXT NOT NULL,
                experience    TEXT
            )
        """)
        # migrate existing DBs
        try:
            conn.execute("ALTER TABLE jobs ADD COLUMN experience TEXT")
        except Exception:
            pass
        # last_seen: most recent scrape that still listed the job. Rows from before
        # this column existed start at first_seen; the next scrape refreshes them.
        try:
            conn.execute("ALTER TABLE jobs ADD COLUMN last_seen TEXT")
        except Exception:
            pass
        conn.execute("UPDATE jobs SET last_seen = first_seen WHERE last_seen IS NULL")
        # Date of each company's last *complete* scrape. A job is active while its
        # last_seen >= that date; older ones are archived (no longer listed).
        conn.execute("""
            CREATE TABLE IF NOT EXISTS company_runs (
                company        TEXT PRIMARY KEY,
                last_full_run  TEXT NOT NULL
            )
        """)
        # Some sites (Microsoft, Motorola, Analog Devices, Intel, Samsung, ...) render
        # posted_date as relative text ("2 hours ago", "Posted Yesterday") that used to
        # get stored verbatim; the frontend then re-derives it against the viewer's
        # current clock, so old jobs never age. Rows already saved that way are stuck
        # forever (INSERT OR IGNORE never updates them), so pin them to the fixed date
        # they were first captured. Applies to any company, not just Microsoft — the
        # failure mode recurs whenever a scraper's source site uses relative dates.
        # No-op once fixed.
        conn.execute("""
            UPDATE jobs SET posted_date = first_seen
            WHERE posted_date LIKE '%ago%'
               OR lower(posted_date) LIKE '%today%'
               OR lower(posted_date) LIKE '%yesterday%'
               OR lower(posted_date) = 'just posted'
        """)
        conn.commit()


def upsert_jobs(jobs: list[dict]) -> int:
    """Insert new jobs and refresh last_seen on existing ones. Returns count of newly inserted."""
    today = date.today().isoformat()
    new_count = 0
    with get_conn() as conn:
        for job in jobs:
            cur = conn.execute(
                """
                INSERT OR IGNORE INTO jobs
                    (role_id, title, team, location, posted_date, url, company, first_seen, experience, last_seen)
                VALUES
                    (:role_id, :title, :team, :location, :posted_date, :url, :company, :first_seen, :experience, :first_seen)
                """,
                {**job, "first_seen": today,
                 "company": job.get("company", "Apple"),
                 "experience": job.get("experience", "")},
            )
            new_count += cur.rowcount
            if not cur.rowcount:
                conn.execute("UPDATE jobs SET last_seen = ? WHERE role_id = ?", (today, job["role_id"]))
        conn.commit()
    return new_count


def record_full_runs(companies) -> None:
    """Mark today as the last full run for every company that returned jobs.

    Companies whose scraper failed (0 jobs) aren't passed in, so their jobs stay active.
    """
    today = date.today().isoformat()
    with get_conn() as conn:
        for company in companies:
            conn.execute(
                "INSERT INTO company_runs (company, last_full_run) VALUES (?, ?) "
                "ON CONFLICT(company) DO UPDATE SET last_full_run = excluded.last_full_run",
                (company, today),
            )
        conn.commit()


def get_new_jobs(since: str = None) -> list[sqlite3.Row]:
    """Return jobs first seen on or after `since` (ISO date). Defaults to today."""
    since = since or date.today().isoformat()
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM jobs WHERE first_seen >= ? ORDER BY first_seen DESC, title",
            (since,),
        ).fetchall()


def get_all_jobs() -> list[sqlite3.Row]:
    """All jobs, with an `archived` flag (1 = not listed in its company's last full scrape)."""
    with get_conn() as conn:
        return conn.execute("""
            SELECT j.*,
                   (r.last_full_run IS NOT NULL AND j.last_seen < r.last_full_run) AS archived
            FROM jobs j LEFT JOIN company_runs r ON r.company = j.company
            ORDER BY j.first_seen DESC, j.title
        """).fetchall()

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
        conn.commit()


def upsert_jobs(jobs: list[dict]) -> int:
    """Insert new jobs, skip existing. Returns count of newly inserted."""
    today = date.today().isoformat()
    new_count = 0
    with get_conn() as conn:
        for job in jobs:
            cur = conn.execute(
                """
                INSERT OR IGNORE INTO jobs
                    (role_id, title, team, location, posted_date, url, company, first_seen, experience)
                VALUES
                    (:role_id, :title, :team, :location, :posted_date, :url, :company, :first_seen, :experience)
                """,
                {**job, "first_seen": today,
                 "company": job.get("company", "Apple"),
                 "experience": job.get("experience", "")},
            )
            new_count += cur.rowcount
        conn.commit()
    return new_count


def get_new_jobs(since: str = None) -> list[sqlite3.Row]:
    """Return jobs first seen on or after `since` (ISO date). Defaults to today."""
    since = since or date.today().isoformat()
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM jobs WHERE first_seen >= ? ORDER BY first_seen DESC, title",
            (since,),
        ).fetchall()


def get_all_jobs() -> list[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute("SELECT * FROM jobs ORDER BY first_seen DESC, title").fetchall()

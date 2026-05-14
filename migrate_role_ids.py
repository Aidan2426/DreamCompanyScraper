"""
One-time migration: add company prefix to role_ids that are missing it.
Run ONCE before next scrape: python migrate_role_ids.py
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "jobs.db"

# company name in DB -> prefix that scrapers now use
MIGRATIONS = [
    ("Apple",      "apple_"),
    ("Google",     "google_"),
    ("Microsoft",  "microsoft_"),
    ("Amazon",     "amazon_"),
    ("Meta",       "meta_"),
    ("Netflix",    "netflix_"),
    ("Nvidia",     "nvidia_"),
    ("Anthropic",  "anthropic_"),
    ("OpenAI",     "openai_"),
]

conn = sqlite3.connect(DB_PATH)
total = 0
for company, prefix in MIGRATIONS:
    cur = conn.execute(
        "UPDATE jobs SET role_id = ? || role_id WHERE company = ? AND role_id NOT LIKE ?",
        (prefix, company, f"{prefix}%"),
    )
    count = cur.rowcount
    total += count
    print(f"{company}: updated {count} rows")

conn.commit()
conn.close()
print(f"\nDone. {total} rows migrated.")

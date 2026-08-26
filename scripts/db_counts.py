import sqlite3
conn = sqlite3.connect('jobs.db')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM jobs')
total = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM jobs WHERE first_seen = '2026-08-06'")
new = cur.fetchone()[0]
print(total, new)

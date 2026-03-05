import sqlite3

db = sqlite3.connect("kino.db", check_same_thread=False)
sql = db.cursor()

sql.execute("""
CREATE TABLE IF NOT EXISTS movies(
code TEXT,
name TEXT,
genre TEXT,
file_id TEXT,
views INTEGER,
premium INTEGER
)
""")

sql.execute("""
CREATE TABLE IF NOT EXISTS users(
user_id INTEGER,
ref INTEGER
)
""")

db.commit()

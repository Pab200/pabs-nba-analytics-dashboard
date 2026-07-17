import sqlite3

conn = sqlite3.connect("nba.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS teams;")
conn.commit()
conn.close()
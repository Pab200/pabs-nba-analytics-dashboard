import sqlite3
import pandas as pd
import glob
import os

conn = sqlite3.connect("nba.db")
cursor = conn.cursor()

csv_files = glob.glob("data/raw/season_stats_*.csv")

for file in csv_files:
    df = pd.read_csv(file)

    # Extract season from filename
    season = os.path.basename(file).replace("season_stats_", "").replace(".csv", "")

    # Remove old rows for this season
    cursor.execute(f"DELETE FROM season_stats WHERE SEASON = '{season}';")

    # Insert fresh data
    df.to_sql("season_stats", conn, if_exists="append", index=False)

    print(f"Reloaded season: {season}")

conn.commit()
conn.close()

import sqlite3
import pandas as pd
import glob
import os

conn = sqlite3.connect("nba.db")
cursor = conn.cursor()

# ------------------------------------------------------------
# 1. RELOAD PLAYER / SEASON STATS
# ------------------------------------------------------------
csv_files = glob.glob("data/raw/season_stats_*.csv")

for file in csv_files:
    df = pd.read_csv(file)

    # Extract season from filename
    season = os.path.basename(file).replace("season_stats_", "").replace(".csv", "")

    # Remove old rows for this season
    cursor.execute(f"DELETE FROM season_stats WHERE SEASON = '{season}';")

    # Insert fresh data
    df.to_sql("season_stats", conn, if_exists="append", index=False)

    print(f"Reloaded season_stats: {season}")


# ------------------------------------------------------------
# 2. RELOAD TEAM GAME STATS (2010-11 to Present)
# ------------------------------------------------------------
# Update "team_game_stats_*.csv" below to match your actual file naming pattern
team_csv_files = glob.glob("data/raw/team_game_stats_*.csv")

for file in team_csv_files:
    df = pd.read_csv(file)

    # Get season value directly from the dataframe column or filename
    if "SEASON" in df.columns and not df.empty:
        season = str(df["SEASON"].iloc[0])
    else:
        season = os.path.basename(file).replace("team_game_stats_", "").replace(".csv", "")

    # Create table if it doesn't exist yet, then remove old rows for this season
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS team_game_stats (
            SEASON_ID TEXT, TEAM_ID INTEGER, TEAM_ABBREVIATION TEXT, TEAM_NAME TEXT,
            GAME_ID TEXT, GAME_DATE TEXT, MATCHUP TEXT, WL TEXT, MIN REAL, FGM REAL,
            FGA REAL, FG_PCT REAL, FG3M REAL, FG3A REAL, FG3_PCT REAL, FTM REAL,
            FTA REAL, FT_PCT REAL, OREB REAL, DREB REAL, REB REAL, AST REAL, STL REAL,
            BLK REAL, TOV REAL, PF REAL, PTS REAL, PLUS_MINUS REAL, VIDEO_AVAILABLE REAL,
            SEASON TEXT
        );
    """)
    cursor.execute(f"DELETE FROM team_game_stats WHERE SEASON = '{season}';")

    # Insert fresh team game data
    df.to_sql("team_game_stats", conn, if_exists="append", index=False)

    print(f"Reloaded team_game_stats: {season}")


conn.commit()
conn.close()
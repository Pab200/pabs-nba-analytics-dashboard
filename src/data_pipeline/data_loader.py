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

# ------------------------------------------------------------
# 3. LOAD PLAYER SHOT DATA (2010-11 to 2025-26)
# ------------------------------------------------------------
import glob
from pathlib import Path

shots_root = Path("data/shots")

# Create table if missing
cursor.execute("""
    CREATE TABLE IF NOT EXISTS player_shots (
        SEASON TEXT,
        SEASON_TYPE TEXT,
        GRID_TYPE TEXT,
        GAME_ID TEXT,
        GAME_EVENT_ID INTEGER,
        PLAYER_ID INTEGER,
        PLAYER_NAME TEXT,
        TEAM_ID INTEGER,
        TEAM_NAME TEXT,
        PERIOD INTEGER,
        MINUTES_REMAINING INTEGER,
        SECONDS_REMAINING INTEGER,
        EVENT_TYPE TEXT,
        ACTION_TYPE TEXT,
        SHOT_TYPE TEXT,
        SHOT_ZONE_BASIC TEXT,
        SHOT_ZONE_AREA TEXT,
        SHOT_ZONE_RANGE TEXT,
        SHOT_DISTANCE REAL,
        LOC_X REAL,
        LOC_Y REAL,
        SHOT_ATTEMPTED_FLAG INTEGER,
        SHOT_MADE_FLAG INTEGER,
        GAME_DATE TEXT,
        HTM TEXT,
        VTM TEXT
    );
""")

# Iterate through seasons
for season_folder in shots_root.iterdir():
    if not season_folder.is_dir():
        continue

    season = season_folder.name  # "2013-14"

    for season_type in ["regular", "playoffs"]:
        type_folder = season_folder / season_type
        if not type_folder.exists():
            continue

        # Delete old rows for this season + type
        cursor.execute(
            "DELETE FROM player_shots WHERE SEASON = ? AND SEASON_TYPE = ?;",
            (season, season_type.capitalize())
        )

        # Load each player's CSV
        csv_files = glob.glob(str(type_folder / "*.csv"))

        for file in csv_files:
            df = pd.read_csv(file)

            # Add metadata columns
            df["SEASON"] = season
            df["SEASON_TYPE"] = season_type.capitalize()

            # Insert into database
            df.to_sql("player_shots", conn, if_exists="append", index=False)

        print(f"Loaded shots: {season} ({season_type})")

conn.commit()
conn.close()
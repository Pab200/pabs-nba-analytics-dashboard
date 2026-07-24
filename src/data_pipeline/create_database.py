# 1. Load CSVs
import pandas as pd
import sqlite3
import os

DATA_DIR = "data/raw"

players = pd.read_csv(f"{DATA_DIR}/players.csv")
teams = pd.read_csv(f"{DATA_DIR}/teams.csv")
teams["year_founded"] = teams["year_founded"].astype("Int64")
teams["year_closed"] = teams["year_closed"].replace("NULL", pd.NA).astype("Int64")
rookies = pd.read_csv(f"{DATA_DIR}/rookies.csv")
season_stats = pd.read_csv(f"{DATA_DIR}/season_stats_2025-26.csv")

print("Players: ", players.shape)
print("Teams: ", teams.shape)
print("Rookies: ", rookies.shape)
print("Season Stats: ", season_stats.shape)

# 2. Connect to SQLite (create nba.db if missing)
DB_PATH = "nba.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 3. Create tables
# 4. Insert DataFrames into tables
players.to_sql("players", conn, if_exists="replace", index=False)
teams.to_sql("teams", conn, if_exists="replace", index=False)
rookies.to_sql("rookies", conn, if_exists="replace", index=False)
season_stats.to_sql("season_stats", conn, if_exists="replace", index=False)

# 5. Print verification
print("Database created successfully!")
print("Players table:", len(players))
print("Teams table:", len(teams))
print("Rookies table:", len(rookies))
print("Season Stats table:", len(season_stats))

# 6. Close connection
conn.close()
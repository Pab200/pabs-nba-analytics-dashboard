# src/fantasy/fetch_game_logs.py

import time
import pandas as pd
from nba_api.stats.endpoints import PlayerGameLog
from src.db import run_query

# ------------------------------------------------------------
# Required headers for stats.nba.com (prevents rate limiting)
# ------------------------------------------------------------
HEADERS = {
    "Host": "stats.nba.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nba.com/",
    "Connection": "keep-alive",
}

# ------------------------------------------------------------
# Safe wrapper around PlayerGameLog
# ------------------------------------------------------------
def safe_player_game_log(player_id, season, retries=3, delay=1.0):
    """
    A safe wrapper around PlayerGameLog that handles:
    - NBA rate limits
    - dropped connections
    - retries
    - required headers
    """
    for attempt in range(retries):
        try:
            logs = PlayerGameLog(
                player_id=player_id,
                season=season,        # KEEP "2015-16" format
                headers=HEADERS
            ).get_data_frames()[0]

            return logs

        except Exception as e:
            print(f"      ⚠️ Attempt {attempt+1}/{retries} failed: {e}")
            time.sleep(delay)

    print("      ❌ All retries failed")
    return pd.DataFrame()

# ------------------------------------------------------------
# Fetch game logs for all players in a season
# ------------------------------------------------------------
def fetch_all_players_game_logs(season: str) -> pd.DataFrame:
    """
    Fetch game logs for all players in a season using PLAYER_ID from your database.
    This avoids missing players and ensures full coverage.
    """

    df_players = run_query(
        """
        SELECT DISTINCT PLAYER_ID, PLAYER_NAME
        FROM season_stats
        WHERE SEASON = ?
        """,
        (season,)
    )

    frames = []

    print(f"\n📅 Season {season}: {len(df_players)} players found")

    for _, row in df_players.iterrows():
        pid = row["PLAYER_ID"]
        name = row["PLAYER_NAME"]

        print(f"   → Fetching logs for {name} (ID: {pid})...")

        logs = safe_player_game_log(pid, season)

        if logs.empty:
            print(f"      ⚠️ No logs returned for {name}")
            continue

        logs["PLAYER_ID"] = pid
        logs["PLAYER_NAME"] = name
        logs["SEASON"] = season

        frames.append(logs)

        print(f"      ✔ Downloaded {len(logs)} games")

        # Prevent rate limiting
        time.sleep(0.6)

    if frames:
        total_rows = sum(len(f) for f in frames)
        print(f"📦 Finished season {season}: {total_rows} total rows")
        return pd.concat(frames, ignore_index=True)

    print(f"⚠️ No logs downloaded for season {season}")
    return pd.DataFrame()
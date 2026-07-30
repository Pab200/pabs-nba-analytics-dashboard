import os
import pandas as pd

RAW_DIR = "data/raw"

def is_modern_season(season_str):
    return int(season_str.split("-")[0]) >= 1996

def is_accurate_data_season(season_str):
    return int(season_str.split("-")[0]) >= 2010

def load_all_seasons():
    """Load all season_stats_*.csv files into one DataFrame"""
    frames = []

    for file in os.listdir(RAW_DIR):
        if file.startswith("season_stats_") and file.endswith(".csv"):
            path = os.path.join(RAW_DIR, file)
            df = pd.read_csv(path)

            # Normalize season format (e.g., "2010-11")
            season = file.replace("season_stats_", "").replace(".csv", "")
            df["SEASON"] = season

            frames.append(df)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)
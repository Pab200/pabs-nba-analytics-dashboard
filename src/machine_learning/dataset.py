import os
import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.machine_learning.features import add_consistency_features, add_boom_bust_features, add_shot_distribution_features
from src.machine_learning.features import add_shot_efficiency_features, add_team_context_features, add_usage_rate_features
from src.machine_learning.features import add_ts_features, add_draft_features, add_age_curve_features
from src.utils import load_all_seasons, RAW_DIR

RAW_DIR = "data/raw"
OUTPUT_DIR = "data/ml"

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

    return pd.concat(frames, ignore_index=True)

def build_training_dataset():
    """Build the Current Season → Next Season training dataset."""

    # 1. Load the combined dataset first
    df = load_all_seasons()

    # Keep only essential columns for Phase 4
    base_cols = [
        "PLAYER_ID", "PLAYER_NAME", "SEASON", "AGE", "GP", "MIN",
        "PTS", "REB", "AST", "STL", "BLK", "TOV",
        "FG_PCT", "FG3_PCT", "FT_PCT",
        "NBA_FANTASY_PTS"
    ]

    df = df[base_cols]

    # Convert season "2010-11 → 2010"
    df["SEASON_START"] = df["SEASON"].apply(lambda s: int(s.split("-")[0]))

    # Create NEXT SEASON table
    df_next = df.copy()
    df_next["SEASON_START"] = df_next["SEASON_START"] - 1  # shift backwards

    # Merge current → next season
    df_merged = df.merge(
        df_next,
        on=["PLAYER_ID", "SEASON_START"],
        suffixes=("_current", "_next")
    )

    # Drop players without next season
    df_merged = df_merged.dropna(subset=["PTS_next"])
    df_merged = df_merged[df_merged["SEASON_START"] >= 1980]
    df_merged = df_merged[df_merged["GP_current"] >= 5]
    df_merged = df_merged[df_merged["MIN_current"] >= 5]

    df_merged = add_consistency_features(df_merged)
    df_merged = add_boom_bust_features(df_merged)
    df_merged = add_shot_distribution_features(df_merged)
    df_merged = add_shot_efficiency_features(df_merged)
    df_merged = add_team_context_features(df_merged)
    df_merged = add_usage_rate_features(df_merged)
    df_merged = add_ts_features(df_merged)
    df_merged = add_draft_features(df_merged)
    df_merged = add_age_curve_features(df_merged)

    # Fill missing numeric values with 0
    numeric_cols = df_merged.select_dtypes(include=["float64", "int64"]).columns
    df_merged[numeric_cols] = df_merged[numeric_cols].fillna(0)

    # Fill missing categorical values with "unknown"
    categorical_cols = df_merged.select_dtypes(include=["object"]).columns
    df_merged[categorical_cols] = df_merged[categorical_cols].fillna("unknown")

    from sklearn.preprocessing import LabelEncoder

    cat_cols = ["CONSISTENCY_LABEL_current", "BOOM_BUST_LABEL_current", "AGE_BUCKET_current"]

    for col in cat_cols:
        if col in df_merged.columns:
            le = LabelEncoder()
            df_merged[col] = le.fit_transform(df_merged[col].astype(str))

    # Save output
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, "training_dataset.csv")
    df_merged.to_csv(out_path, index=False)

    print(f"Training dataset saved to: {out_path}")
    print(f"Rows: {len(df_merged)}")

if __name__ == "__main__":
    build_training_dataset()
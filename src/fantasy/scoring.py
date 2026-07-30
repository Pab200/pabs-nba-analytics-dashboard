# src/fantasy/scoring.py

import pandas as pd

# ------------------------------------------------------------
# Default ESPN-style scoring (user can override in UI)
# ------------------------------------------------------------
DEFAULT_SCORING = {
    "PTS": 1.0,
    "REB": 1.0,
    "AST": 2.0,
    "STL": 4.0,
    "BLK": 4.0,
    "TOV": -2.0,
}

# ------------------------------------------------------------
# Core fantasy calculation
# ------------------------------------------------------------
def compute_fantasy_points(df: pd.DataFrame, scoring: dict = None) -> pd.DataFrame:
    if scoring is None:
        scoring = DEFAULT_SCORING

    required_cols = ["PTS", "REB", "AST", "STL", "BLK", "TOV", "GP"]
    if not set(required_cols).issubset(df.columns):
        raise ValueError("DataFrame missing required columns for fantasy scoring.")

    # Fantasy points per game (correct for your dataset)
    df["FANTASY_PPG"] = (
        df["PTS"] * scoring["PTS"]
        + df["REB"] * scoring["REB"]
        + df["AST"] * scoring["AST"]
        + df["STL"] * scoring["STL"]
        + df["BLK"] * scoring["BLK"]
        + df["TOV"] * scoring["TOV"]
    )

    # Total fantasy points = per-game * games played
    df["FANTASY_TOTAL"] = df["FANTASY_PPG"] * df["GP"]

    return df

# ------------------------------------------------------------
# Helper: apply scoring to season_stats query results
# ------------------------------------------------------------
def add_fantasy_scores(df: pd.DataFrame, scoring: dict = None) -> pd.DataFrame:
    """
    Wrapper to compute fantasy scores on any season_stats DataFrame.
    """
    return compute_fantasy_points(df, scoring)
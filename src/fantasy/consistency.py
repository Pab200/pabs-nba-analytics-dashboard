# src/fantasy/consistency.py

import pandas as pd
import numpy as np

from src.fantasy.scoring import compute_fantasy_points

# ------------------------------------------------------------
# Compute fantasy points for each game
# ------------------------------------------------------------
def add_fantasy_to_game_logs(df_games: pd.DataFrame, scoring: dict) -> pd.DataFrame:
    """
    Adds fantasy points to each game log using the scoring engine.
    df_games must contain per-game stats: PTS, REB, AST, STL, BLK, TOV.
    """
    df = df_games.copy()

    df["FANTASY_PTS"] = (
        df["PTS"] * scoring["PTS"]
        + df["REB"] * scoring["REB"]
        + df["AST"] * scoring["AST"]
        + df["STL"] * scoring["STL"]
        + df["BLK"] * scoring["BLK"]
        + df["TOV"] * scoring["TOV"]
    )

    return df

# ------------------------------------------------------------
# Consistency metrics
# ------------------------------------------------------------
def compute_consistency(df_games: pd.DataFrame) -> dict:
    """
    Computes consistency metric for a player's game logs.
    Returns:
        - mean fantasy points
        - standard deviation
        - coefficient of variation
        - boom/bust classification
    """

    fantasy = df_games["FANTASY_PTS"]

    mean_fp = fantasy.mean()
    std_fp = fantasy.std(ddof=0)
    cv_fp = std_fp / mean_fp if mean_fp != 0 else np.nan

    # Boom/Bust classification
    if std_fp > mean_fp * 0.40:
        label = "Boom/Bust"
    elif std_fp < mean_fp * 0.20:
        label = "Reliable"
    else:
        label = "Moderate Variance"

    return {
        "mean_fp": mean_fp,
        "std_fp": std_fp,
        "cv_fp": cv_fp,
        "label": label
    }

# ------------------------------------------------------------
# Full pipeline for a single player
# ------------------------------------------------------------
def analyze_player_consistency(df_games: pd.DataFrame, scoring: dict):
    """
    Adds fantasy points to game logs and computes consistency metrics.
    """
    df = add_fantasy_to_game_logs(df_games, scoring)
    metrics = compute_consistency(df)
    return df, metrics
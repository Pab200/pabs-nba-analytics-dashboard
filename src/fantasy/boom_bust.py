# src/fantasy/boom_bust.py

import pandas as pd
import numpy as np

# ------------------------------------------------------------
# Boom/Bust thresholds (percentile-based)
# ------------------------------------------------------------
def compute_boom_bust(df_games: pd.DataFrame):
    fp = df_games["FANTASY_PTS"]

    boom_threshold = np.percentile(fp, 80)
    bust_threshold = np.percentile(fp, 20)

    df= df_games.copy()
    df["RESULT"] = df["FANTASY_PTS"].apply(
        lambda x: "Boom"  if x >= boom_threshold
        else ("Bust" if x <= bust_threshold else "Neutral")
    )

    boom_rate = (df["RESULT"] == "Boom").mean()
    bust_rate = (df["RESULT"] == "Bust").mean()
    neutral_rate = (df["RESULT"] == "Neutral").mean()

    return df, {
        "boom_threshold": boom_threshold,
        "bust_threshold": bust_threshold,
        "boom_rate": boom_rate,
        "bust_rate": bust_rate,
        "neutral_rate": neutral_rate
    }

# ------------------------------------------------------------
# Minutes-adjusted reliability
# ------------------------------------------------------------
def compute_minutes_reliability(df_games: pd.DataFrame):
    mean_min = df_games["MIN"].mean()
    reliability = mean_min / 36 # 36-minute baseline
    return mean_min, reliability

# ------------------------------------------------------------
# Final classification
# ------------------------------------------------------------
def classify_player(boom_rate, bust_rate, reliability):
    if reliability >= 0.75:
        if boom_rate >= 0.30:
            return "High-Ceiling Starter"
        elif bust_rate >= 0.30:
            return "Volatile Starter"
        else:
            return "Reliable Starter"

    else:
        if boom_rate >= 0.30:
            return "High-Upside Bench Player"
        elif bust_rate >= 0.30:
            return "Low-Floor Bench Player"
        else:
            return "Low-Ceiling Role Player"

# ------------------------------------------------------------
# Full pipeline
# ------------------------------------------------------------
def analyze_boom_bust(df_games: pd.DataFrame):
    df_bb, bb_metrics = compute_boom_bust(df_games)
    mean_min, reliability = compute_minutes_reliability(df_games)
    classification = classify_player(
        bb_metrics["boom_rate"],
        bb_metrics["bust_rate"],
        reliability
    )

    return df_bb, {
        **bb_metrics,
        "mean_minutes": mean_min,
        "minutes_reliability": reliability,
        "classification": classification
    }
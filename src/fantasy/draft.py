# src/fantasy/draft.py

import pandas as pd
import numpy as np

from src.fantasy.consistency import analyze_player_consistency
from src.fantasy.boom_bust import analyze_boom_bust

# ------------------------------------------------------------
# Draft Score
# ------------------------------------------------------------
def compute_draft_score(fp_ppg, consistency, boom_rate, reliability):
    return (
        fp_ppg * 0.45 +             # ceiling
        (1 - consistency) * 0.20 +  # lower consistency = higher score
        boom_rate * 0.20 +          # upside
        reliability * 0.15          # role stability
    )

# ------------------------------------------------------------
# Tier Assignment
# ------------------------------------------------------------
def assign_tier(score):
    if score >= 35:
        return "S"
    elif score >= 28:
        return "A"
    elif score >= 22:
        return "B"
    elif score >= 16:
        return "C"
    else:
        return "D"

# ------------------------------------------------------------
# Risk Rating
# ------------------------------------------------------------
def compute_risk(std_fp, bust_rate):
    risk = (
        std_fp * 0.6 +
        bust_rate * 0.4
    )
    if risk >= 20:
        return "High"
    elif risk >= 12:
        return "Medium"
    else:
        return "Low"

# ------------------------------------------------------------
# Role Projection
# ------------------------------------------------------------
def compute_role(reliability):
    if reliability >= 0.80:
        return "Full-Time Starter"
    elif reliability >= 0.60:
        return "Strong Rotation"
    elif reliability >= 0.40:
        return "Bench Contributor"
    else:
        return "Fringe Rotation"

# ------------------------------------------------------------
# Full Draft Analysis
# ------------------------------------------------------------
def analyze_player_draft(df_player, scoring):
    df_player = df_player.copy()

    # Calculate Fantasy PPG & ensure FANTASY_PTS column exists
    if "FANTASY_PTS" not in df_player.columns:
        df_player["FANTASY_PTS"] = (
            df_player["PTS"] * scoring.get("PTS", 0) +
            df_player["REB"] * scoring.get("REB", 0) +
            df_player["AST"] * scoring.get("AST", 0) +
            df_player["STL"] * scoring.get("STL", 0) +
            df_player["BLK"] * scoring.get("BLK", 0) +
            df_player["TOV"] * scoring.get("TOV", 0)
        )

    fp_ppg = df_player["FANTASY_PTS"].mean()

    # Consistency
    _, cons_metrics = analyze_player_consistency(df_player, scoring)
    consistency = cons_metrics["cv_fp"]
    std_fp = cons_metrics["std_fp"]

    # Boom/Bust
    df_bb, bb_metrics = analyze_boom_bust(df_player)
    boom_rate = bb_metrics["boom_rate"]
    bust_rate = bb_metrics["bust_rate"]
    
    # Safe retrieval for reliability metric across various implementations
    reliability = bb_metrics.get("minutes_reliability", bb_metrics.get("reliability", 0.0))

    # Draft Score
    draft_score = compute_draft_score(fp_ppg, consistency, boom_rate, reliability)

    # Tier
    tier = assign_tier(draft_score)

    # Risk
    risk = compute_risk(std_fp, bust_rate)

    # Role
    role = compute_role(reliability)

    return {
        "fp_ppg": fp_ppg,
        "consistency": consistency,
        "std_fp": std_fp,
        "boom_rate": boom_rate,
        "bust_rate": bust_rate,
        "reliability": reliability,
        "draft_score": draft_score,
        "tier": tier,
        "risk": risk,
        "role": role
    }
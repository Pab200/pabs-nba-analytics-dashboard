# src/fantasy/sleepers.py

import pandas as pd
import numpy as np

from src.fantasy.boom_bust import analyze_boom_bust

# ------------------------------------------------------------
# Recent trend score (last 5 games)
# ------------------------------------------------------------
def compute_recent_trend(df_games):
    recent = df_games.tail(5)["FANTASY_PTS"]
    if len(recent) == 0:
        return 0
    return (recent.mean() - df_games["FANTASY_PTS"].mean()) / 10 # scaled

# ------------------------------------------------------------
# Sleeper score
# ------------------------------------------------------------
def compute_sleeper_score(boom_rate, bust_rate, reliability, trend_score):
    return (
        boom_rate * 0.40 +
        reliability * 0.20 +
        trend_score * 0.20 +
        (1 - bust_rate) * 0.20
    )

# ------------------------------------------------------------
# Breakout probability
# ------------------------------------------------------------
def compute_breakout_probability(boom_rate, reliability):
    return boom_rate * reliability

# ------------------------------------------------------------
# Full sleeper analysis for one player
# ------------------------------------------------------------
def analyze_player_sleeper(df_games):
    df_bb, bb_metrics = analyze_boom_bust(df_games)

    boom_rate = bb_metrics["boom_rate"]
    bust_rate = bb_metrics["bust_rate"]
    reliability = bb_metrics["minutes_reliability"]

    trend_score = compute_recent_trend(df_games)
    sleeper_score = compute_sleeper_score(boom_rate, bust_rate, reliability, trend_score)
    breakout_prob = compute_breakout_probability(boom_rate, reliability)

    return {
        "boom_rate": boom_rate,
        "bust_rate": bust_rate,
        "reliability": reliability,
        "trend_score": trend_score,
        "sleeper_score": sleeper_score,
        "breakout_prob": breakout_prob,
        "classification": bb_metrics["classification"]
    }
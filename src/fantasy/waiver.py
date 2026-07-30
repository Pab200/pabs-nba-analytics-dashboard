# src/fantasy/waiver.py

import pandas as pd
import numpy as np

from src.fantasy.sleepers import analyze_player_sleeper

# ------------------------------------------------------------
# Availability score (updated to eliminate stars)
# ------------------------------------------------------------
def compute_availability(df_player):
    gp = len(df_player)
    mean_min = df_player["MIN"].mean()
    fantasy_ppg = df_player["FANTASY_PTS"].mean()

    # Reliability = proxy for starter status
    reliability = mean_min / 36  # 0–1

    # HARD FILTER: Stars should NEVER appear on waivers
    if reliability >= 0.80 and fantasy_ppg >= 24:
        return 0.02  # near-zero availability

    # Minutes & GP still matter
    minutes_component = (1 - reliability) * 0.35
    games_component = (1 - (gp / 82)) * 0.25

    # Fantasy PPG availability curve:
    # - Peak availability around 22 FPPG
    # - Drops below 15 (too low)
    # - Drops above 28 (too good to be on waivers)
    if fantasy_ppg < 15:
        fppg_component = 0.15
    elif 15 <= fantasy_ppg <= 28:
        fppg_component = 1 - abs(fantasy_ppg - 22) / 7
    else:
        fppg_component = 0.10

    score = (
        minutes_component * 0.40 +
        games_component * 0.20 +
        fppg_component * 0.40
    )

    return max(0, min(score, 1))  # clamp 0–1


# ------------------------------------------------------------
# Opportunity score
# ------------------------------------------------------------
def compute_opportunity(sleeper_metrics):
    return (
        sleeper_metrics["sleeper_score"] * 0.50 +
        sleeper_metrics["breakout_prob"] * 0.50
    )


# ------------------------------------------------------------
# Waiver wire score
# ------------------------------------------------------------
def compute_waiver_score(availability, opportunity):
    return (
        opportunity * 0.60 +
        availability * 0.40
    )


# ------------------------------------------------------------
# Full waiver wire analysis for one player
# ------------------------------------------------------------
def analyze_player_waiver(df_player):
    sleeper_metrics = analyze_player_sleeper(df_player)

    availability = compute_availability(df_player)
    opportunity = compute_opportunity(sleeper_metrics)
    waiver_score = compute_waiver_score(availability, opportunity)

    return {
        "availability": availability,
        "opportunity": opportunity,
        "waiver_score": waiver_score,
        **sleeper_metrics
    }

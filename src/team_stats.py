"""
Team season statistics module.

Calculates team-level total and per-game stats by weighting player per-game averages 
by their games played (`GP`) across the roster.
"""

import numpy as np
import pandas as pd
from src.db import run_query
from src.utils import is_modern_season, is_accurate_data_season


def estimate_possessions(fga, fta, oreb, tov):
    """
    Standard NBA possession formula.
    """
    return fga + 0.44 * fta - oreb + tov


def get_team_season_stats(team: str, season: str) -> pd.DataFrame:
    """
    Returns team-level season statistics. 
    Computes true SEASON TOTALS and then derives Per-Game Averages.
    """
    
    # Query all player rows for this team and season
    df_players = run_query(
        """
        SELECT 
            TEAM_ABBREVIATION,
            GP,
            PTS,
            FGM,
            FGA,
            FTM,
            FTA,
            OREB,
            DREB,
            REB,
            AST,
            TOV,
            FG3A,
            PLUS_MINUS,
            MIN
        FROM season_stats
        WHERE TEAM_ABBREVIATION = ?
        AND SEASON = ?
        """,
        (team, season)
    )

    if df_players.empty or df_players["TEAM_ABBREVIATION"].dropna().empty:
        return pd.DataFrame()

    # Determine the team's total games played (max GP on the roster)
    team_games = df_players["GP"].max()
    if not team_games or team_games <= 0:
        return pd.DataFrame()

    metrics = ["PTS", "FGM", "FGA", "FTM", "FTA", "OREB", "DREB", "REB", "AST", "TOV", "FG3A", "PLUS_MINUS", "MIN"]
    
    team_data = {"TEAM_ABBREVIATION": [team], "GAMES_PLAYED": [team_games]}
    
    for col in metrics:
        if col in df_players.columns:
            # CORRECT MATH: (Player Stat Per Game * Player Games Played) summed for the whole team
            # This yields the TRUE TOTAL for the team across the entire season.
            total_season_stat = (df_players[col] * df_players["GP"]).sum()
            team_data[f"TEAM_{col}"] = [total_season_stat]
        else:
            team_data[f"TEAM_{col}"] = [None]

    df = pd.DataFrame(team_data)

    # To calculate ratings and pace cleanly, we convert the season totals 
    # to per-game team averages for the possession formulas:
    gp = df["GAMES_PLAYED"].iloc[0]
    team_pts_pg = df["TEAM_PTS"].iloc[0] / gp
    team_fga_pg = df["TEAM_FGA"].iloc[0] / gp
    team_fta_pg = df["TEAM_FTA"].iloc[0] / gp
    team_oreb_pg = df["TEAM_OREB"].iloc[0] / gp
    team_tov_pg = df["TEAM_TOV"].iloc[0] / gp
    team_min_pg = df["TEAM_MIN"].iloc[0] / gp

    # Possessions (per game basis)
    tm_poss = estimate_possessions(team_fga_pg, team_fta_pg, team_oreb_pg, team_tov_pg)
    df["TEAM_POSS"] = tm_poss

    df["OFF_RATING"] = np.where(tm_poss > 0, 100 * team_pts_pg / tm_poss, None)

    # Defensive Rating (estimated using PLUS_MINUS totals if available)
    if is_modern_season(season) and df["TEAM_PLUS_MINUS"].iloc[0] is not None:
        team_pts_allowed_pg = team_pts_pg - (df["TEAM_PLUS_MINUS"].iloc[0] / gp)
        df["DEF_RATING"] = np.where(tm_poss > 0, 100 * team_pts_allowed_pg / tm_poss, None)
    else:
        df["DEF_RATING"] = None

    df["PACE"] = np.where(team_min_pg > 0, 48 * (tm_poss / (team_min_pg / 5)), None)

    # JSON safety cleanup
    return df.replace([np.inf, -np.inf], np.nan).replace({np.nan: None})
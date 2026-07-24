"""
Team season statistics module.

Handles:
- Modern seasons (2010–present) with opponent data
- Mid-era seasons (1996–2009) with partial data
- Older seasons (pre-1996) with limited data
"""

import numpy as np
import pandas as pd
from src.db import run_query
from src.utils import is_modern_season, is_accurate_data_season


# ------------------------------------------------------------
# Helper: Possession formulas
# ------------------------------------------------------------
def estimate_possessions(fga, fta, oreb, tov):
    """
    Standard NBA possession formula.
    """
    return fga + 0.44 * fta - oreb + tov


# ------------------------------------------------------------
# Main function: Team Season Stats
# ------------------------------------------------------------
def get_team_season_stats(team: str, season: str) -> pd.DataFrame:
    """
    Returns team-level season statistics including:
    - Offensive Rating
    - Defensive Rating
    - Pace
    - Estimated Possessions

    Automatically chooses the correct data source depending on season.
    """

    # ------------------------------------------------------------
    # CASE 1 — Modern seasons (2010–present)
    # Full opponent data available
    # ------------------------------------------------------------
    if is_accurate_data_season(season):
        df = run_query(
            """
            SELECT 
                t1.TEAM_ABBREVIATION,
                SUM(t1.PTS) AS TEAM_PTS,
                SUM(t1.FGM) AS TEAM_FGM,
                SUM(t1.FGA) AS TEAM_FGA,
                SUM(t1.FTM) AS TEAM_FTM,
                SUM(t1.FTA) AS TEAM_FTA,
                SUM(t1.OREB) AS TEAM_OREB,
                SUM(t1.DREB) AS TEAM_DREB,
                SUM(t1.REB) AS TEAM_REB,
                SUM(t1.AST) AS TEAM_AST,
                SUM(t1.TOV) AS TEAM_TOV,
                SUM(t1.FG3A) AS TEAM_FG3A,
                SUM(t1.PLUS_MINUS) AS TEAM_PLUS_MINUS,
                SUM(t1.MIN) AS TEAM_MIN,

                -- Opponent stats
                SUM(t2.PTS) AS OPP_PTS,
                SUM(t2.FGA) AS OPP_FGA,
                SUM(t2.FTA) AS OPP_FTA,
                SUM(t2.OREB) AS OPP_OREB,
                SUM(t2.TOV) AS OPP_TOV

            FROM team_game_stats t1
            JOIN team_game_stats t2
                ON t1.GAME_ID = t2.GAME_ID
                AND t1.TEAM_ID != t2.TEAM_ID

            WHERE t1.TEAM_ABBREVIATION = ?
            AND t1.SEASON = ?

            GROUP BY t1.TEAM_ABBREVIATION
            """,
            (team, season)
        )

        if df.empty:
            return df

        # Possessions (modern formula)
        tm_poss = estimate_possessions(
            df["TEAM_FGA"], df["TEAM_FTA"], df["TEAM_OREB"], df["TEAM_TOV"]
        )
        opp_poss = estimate_possessions(
            df["OPP_FGA"], df["OPP_FTA"], df["OPP_OREB"], df["OPP_TOV"]
        )

        df["TEAM_POSS"] = 0.5 * (tm_poss + opp_poss)

        df["OFF_RATING"] = 100 * df["TEAM_PTS"] / df["TEAM_POSS"]
        df["DEF_RATING"] = 100 * df["OPP_PTS"] / df["TEAM_POSS"]
        df["PACE"] = 48 * (df["TEAM_POSS"] / (df["TEAM_MIN"] / 5))

        return df

    # ------------------------------------------------------------
    # CASE 2 — Mid-era seasons (1996–2009)
    # No opponent data, but PLUS_MINUS exists
    # ------------------------------------------------------------
    df = run_query(
        """
        SELECT 
            TEAM_ABBREVIATION,
            SUM(PTS) AS TEAM_PTS,
            SUM(FGM) AS TEAM_FGM,
            SUM(FGA) AS TEAM_FGA,
            SUM(FTM) AS TEAM_FTM,
            SUM(FTA) AS TEAM_FTA,
            SUM(OREB) AS TEAM_OREB,
            SUM(DREB) AS TEAM_DREB,
            SUM(REB) AS TEAM_REB,
            SUM(AST) AS TEAM_AST,
            SUM(TOV) AS TEAM_TOV,
            SUM(FG3A) AS TEAM_FG3A,
            SUM(PLUS_MINUS) AS TEAM_PLUS_MINUS,
            SUM(MIN) AS TEAM_MIN
        FROM season_stats
        WHERE TEAM_ABBREVIATION = ?
        AND SEASON = ?
        """,
        (team, season)
    )

    if df.empty:
        return df

    # Possessions (fallback formula)
    df["TEAM_POSS"] = estimate_possessions(
        df["TEAM_FGA"], df["TEAM_FTA"], df["TEAM_OREB"], df["TEAM_TOV"]
    )

    df["OFF_RATING"] = 100 * df["TEAM_PTS"] / df["TEAM_POSS"]

    # Defensive Rating (estimated)
    if is_modern_season(season):
        df["TEAM_PTS_ALLOWED"] = df["TEAM_PTS"] - df["TEAM_PLUS_MINUS"]
        df["DEF_RATING"] = 100 * df["TEAM_PTS_ALLOWED"] / df["TEAM_POSS"]
    else:
        df["DEF_RATING"] = np.nan

    df["PACE"] = 48 * (df["TEAM_POSS"] / (df["TEAM_MIN"] / 5))

    return df

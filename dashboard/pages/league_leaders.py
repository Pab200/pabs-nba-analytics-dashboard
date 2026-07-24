import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from src.db import run_query
from src.metrics import add_advanced_metrics
from src.colors import get_primary, get_secondary
from src.utils import is_modern_season
from dashboard.components.styling import color_team_table


def render(selected_season, seasons):
    st.header("🏀 League Leaders")
    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------------------
    # Helper: team colors
    # ------------------------------------------------------------
    def team_colors(df):
        prim = [get_primary(t) for t in df["TEAM_ABBREVIATION"]]
        sec = [get_secondary(t) for t in df["TEAM_ABBREVIATION"]]
        return prim, sec

    # ------------------------------------------------------------
    # POINTS
    # ------------------------------------------------------------
    pts_metric = st.radio(
        "Points metric",
        ["Total Points", "Points Per Game"],
        horizontal=True
    )

    if pts_metric == "Total Points":
        df_points = run_query(
            """
            SELECT PLAYER_NAME, PTS * GP AS TOTAL_POINTS, TEAM_ABBREVIATION
            FROM season_stats
            WHERE SEASON = ?
            ORDER BY TOTAL_POINTS DESC
            LIMIT 10
            """,
            (selected_season,)
        )
        y_col = "TOTAL_POINTS"
        title = "🔥 Top Scorers (Total Points)"
    else:
        df_points = run_query(
            """
            SELECT PLAYER_NAME, PTS AS PPG, PTS * GP AS TOTAL_POINTS, TEAM_ABBREVIATION
            FROM season_stats
            WHERE SEASON = ?
            ORDER BY TOTAL_POINTS DESC
            LIMIT 10
            """,
            (selected_season,)
        )
        y_col = "PPG"
        title = "🔥 Top Scorers (Points Per Game)"

    prim, sec = team_colors(df_points)

    st.subheader(title)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df_points["PLAYER_NAME"], df_points[y_col], color=prim, edgecolor=sec, linewidth=3)
    ax.set_xticklabels(df_points["PLAYER_NAME"], rotation=45)
    st.pyplot(fig)
    st.markdown("<br><br>", unsafe_allow_html=True)

    # ------------------------------------------------------------
    # REBOUNDS
    # ------------------------------------------------------------
    reb_metric = st.radio(
        "Rebounds metric",
        ["Total Rebounds", "Rebounds Per Game", "Offensive REB Per Game", "Defensive REB Per Game"],
        horizontal=True
    )

    df_reb = run_query(
        """
        SELECT PLAYER_NAME,
               REB * GP AS TOTAL_REBOUNDS,
               REB AS REB_PG,
               OREB AS OREB_PG,
               DREB AS DREB_PG,
               TEAM_ABBREVIATION
        FROM season_stats
        WHERE SEASON = ?
        ORDER BY TOTAL_REBOUNDS DESC
        LIMIT 10
        """,
        (selected_season,)
    )

    metric_map = {
        "Total Rebounds": ("TOTAL_REBOUNDS", "💪 Top Rebounders (Total)"),
        "Rebounds Per Game": ("REB_PG", "💪 Top Rebounders (Per Game)"),
        "Offensive REB Per Game": ("OREB_PG", "💪 Top Offensive Rebounders"),
        "Defensive REB Per Game": ("DREB_PG", "💪 Top Defensive Rebounders"),
    }

    y_col, title = metric_map[reb_metric]
    prim, sec = team_colors(df_reb)

    st.subheader(title)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df_reb["PLAYER_NAME"], df_reb[y_col], color=prim, edgecolor=sec, linewidth=3)
    ax.set_xticklabels(df_reb["PLAYER_NAME"], rotation=45)
    st.pyplot(fig)
    st.markdown("<br><br>", unsafe_allow_html=True)

    # ------------------------------------------------------------
    # ASSISTS
    # ------------------------------------------------------------
    ast_metric = st.radio(
        "Assists metric",
        ["Total Assists", "Assists Per Game"],
        horizontal=True
    )

    df_ast = run_query(
        """
        SELECT PLAYER_NAME,
               AST * GP AS TOTAL_ASSISTS,
               AST AS AST_PG,
               TEAM_ABBREVIATION
        FROM season_stats
        WHERE SEASON = ?
        ORDER BY TOTAL_ASSISTS DESC
        LIMIT 10
        """,
        (selected_season,)
    )

    if ast_metric == "Total Assists":
        y_col, title = "TOTAL_ASSISTS", "🎯 Top Assist Leaders (Total)"
    else:
        y_col, title = "AST_PG", "🎯 Top Assist Leaders (Per Game)"

    prim, sec = team_colors(df_ast)

    st.subheader(title)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df_ast["PLAYER_NAME"], df_ast[y_col], color=prim, edgecolor=sec, linewidth=3)
    ax.set_xticklabels(df_ast["PLAYER_NAME"], rotation=45)
    st.pyplot(fig)
    st.markdown("<br><br>", unsafe_allow_html=True)

    # ------------------------------------------------------------
    # SHOOTING METRICS
    # ------------------------------------------------------------
    fg_metric = st.radio(
        "Shooting metric",
        ["FG%", "3P%", "FGA", "FGM"],
        horizontal=True
    )

    df_fg = run_query(
        """
        SELECT PLAYER_NAME, FG_PCT, FG3_PCT, FGA, FGM, TEAM_ABBREVIATION
        FROM season_stats
        WHERE SEASON = ?
        AND MIN >= 30
        ORDER BY FG_PCT DESC
        LIMIT 10
        """,
        (selected_season,)
    )

    metric_map = {
        "FG%": ("FG_PCT", "🎯 Field Goal Percentage (min 30 MPG)"),
        "3P%": ("FG3_PCT", "🎯 Three-Point Percentage (min 30 MPG)"),
        "FGA": ("FGA", "🎯 Field Goal Attempts (min 30 MPG)"),
        "FGM": ("FGM", "🎯 Field Goals Made (min 30 MPG)"),
    }

    y_col, title = metric_map[fg_metric]
    prim, sec = team_colors(df_fg)

    st.subheader(title)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df_fg["PLAYER_NAME"], df_fg[y_col], color=prim, edgecolor=sec, linewidth=3)
    ax.set_xticklabels(df_fg["PLAYER_NAME"], rotation=45)
    st.pyplot(fig)
    st.markdown("<br><br>", unsafe_allow_html=True)

    # ------------------------------------------------------------
    # FANTASY POINTS
    # ------------------------------------------------------------
    st.subheader("📊 Other League Leaders")

    fantasy_metric = st.radio(
        "Fantasy metric",
        ["Total Fantasy Points", "Fantasy Points Per Game"],
        horizontal=True
    )

    if is_modern_season(selected_season):
        df_fantasy = run_query(
            """
            SELECT PLAYER_NAME,
                   NBA_FANTASY_PTS * GP AS TOTAL_FANTASY,
                   NBA_FANTASY_PTS AS FANTASY_PG,
                   TEAM_ABBREVIATION
            FROM season_stats
            WHERE SEASON = ?
            ORDER BY TOTAL_FANTASY DESC
            LIMIT 10
            """,
            (selected_season,)
        )

        prim, sec = team_colors(df_fantasy)
        y_col = "TOTAL_FANTASY" if fantasy_metric == "Total Fantasy Points" else "FANTASY_PG"

        fig, ax = plt.subplots(figsize=(19, 6))
        ax.bar(df_fantasy["PLAYER_NAME"], df_fantasy[y_col], color=prim, edgecolor=sec, linewidth=3)
        ax.set_xticklabels(df_fantasy["PLAYER_NAME"], rotation=45)
        st.pyplot(fig)
    else:
        st.warning("Fantasy points are unavailable before 1996–97.")

    # ------------------------------------------------------------
    # STEALS
    # ------------------------------------------------------------
    steals_metric = st.radio(
        "Steals metric",
        ["Total Steals", "Steals Per Game"],
        horizontal=True
    )

    df_stl = run_query(
        """
        SELECT PLAYER_NAME,
               STL * GP AS TOTAL_STEALS,
               STL AS STL_PG,
               TEAM_ABBREVIATION
        FROM season_stats
        WHERE SEASON = ?
        ORDER BY TOTAL_STEALS DESC
        LIMIT 10
        """,
        (selected_season,)
    )

    prim, sec = team_colors(df_stl)
    y_col = "TOTAL_STEALS" if steals_metric == "Total Steals" else "STL_PG"

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df_stl["PLAYER_NAME"], df_stl[y_col], color=prim, edgecolor=sec, linewidth=3)
    ax.set_xticklabels(df_stl["PLAYER_NAME"], rotation=45)
    st.pyplot(fig)

    # ------------------------------------------------------------
    # BLOCKS
    # ------------------------------------------------------------
    blocks_metric = st.radio(
        "Blocks metric",
        ["Total Blocks", "Blocks Per Game"],
        horizontal=True
    )

    df_blk = run_query(
        """
        SELECT PLAYER_NAME,
               BLK * GP AS TOTAL_BLOCKS,
               BLK AS BLK_PG,
               TEAM_ABBREVIATION
        FROM season_stats
        WHERE SEASON = ?
        ORDER BY TOTAL_BLOCKS DESC
        LIMIT 10
        """,
        (selected_season,)
    )

    prim, sec = team_colors(df_blk)
    y_col = "TOTAL_BLOCKS" if blocks_metric == "Total Blocks" else "BLK_PG"

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df_blk["PLAYER_NAME"], df_blk[y_col], color=prim, edgecolor=sec, linewidth=3)
    ax.set_xticklabels(df_blk["PLAYER_NAME"], rotation=45)
    st.pyplot(fig)

    # ------------------------------------------------------------
    # TURNOVERS
    # ------------------------------------------------------------
    tov_metric = st.radio(
        "Turnovers metric",
        ["Total Turnovers", "Turnovers Per Game"],
        horizontal=True
    )

    df_tov = run_query(
        """
        SELECT PLAYER_NAME,
               TOV * GP AS TOTAL_TOV,
               TOV AS TOV_PG,
               TEAM_ABBREVIATION
        FROM season_stats
        WHERE SEASON = ?
        ORDER BY TOTAL_TOV DESC
        LIMIT 10
        """,
        (selected_season,)
    )

    prim, sec = team_colors(df_tov)
    y_col = "TOTAL_TOV" if tov_metric == "Total Turnovers" else "TOV_PG"

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df_tov["PLAYER_NAME"], df_tov[y_col], color=prim, edgecolor=sec, linewidth=3)
    ax.set_xticklabels(df_tov["PLAYER_NAME"], rotation=45)
    st.pyplot(fig)

    # ------------------------------------------------------------
    # MINUTES
    # ------------------------------------------------------------
    min_metric = st.radio(
        "Minutes metric",
        ["Total Minutes", "Minutes Per Game"],
        horizontal=True
    )

    df_min = run_query(
        """
        SELECT PLAYER_NAME,
               MIN * GP AS TOTAL_MIN,
               MIN AS MIN_PG,
               TEAM_ABBREVIATION
        FROM season_stats
        WHERE SEASON = ?
        ORDER BY TOTAL_MIN DESC
        LIMIT 10
        """,
        (selected_season,)
    )

    prim, sec = team_colors(df_min)
    y_col = "TOTAL_MIN" if min_metric == "Total Minutes" else "MIN_PG"

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df_min["PLAYER_NAME"], df_min[y_col], color=prim, edgecolor=sec, linewidth=3)
    ax.set_xticklabels(df_min["PLAYER_NAME"], rotation=45)
    st.pyplot(fig)

    # ------------------------------------------------------------
    # ADVANCED METRICS
    # ------------------------------------------------------------
    adv_metric = st.radio(
        "Advanced metric",
        ["TS%", "eFG%", "AST/TOV"],
        horizontal=True
    )

    df_adv = run_query(
        """
        SELECT PLAYER_NAME, TEAM_ABBREVIATION,
               PTS, FGA, FTA, FGM, FG3M, AST, TOV
        FROM season_stats
        WHERE SEASON = ?
        AND MIN >= 30
        """,
        (selected_season,)
    )

    df_adv = add_advanced_metrics(df_adv)

    metric_map = {
        "TS%": ("TS_PCT", "🔥 True Shooting % Leaders"),
        "eFG%": ("EFG_PCT", "🔥 Effective FG % Leaders"),
        "AST/TOV": ("AST_TOV", "🔥 Assist-to-Turnover Ratio Leaders"),
    }

    y_col, title = metric_map[adv_metric]
    df_plot = df_adv.sort_values(y_col, ascending=False).head(10)

    prim, sec = team_colors(df_plot)

    st.subheader(title)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df_plot["PLAYER_NAME"], df_plot[y_col], color=prim, edgecolor=sec, linewidth=3)
    ax.set_xticklabels(df_plot["PLAYER_NAME"], rotation=45)
    st.pyplot(fig)

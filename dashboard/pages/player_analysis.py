import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from src.db import run_query
from src.metrics import add_advanced_metrics
from src.colors import get_primary, get_secondary
from dashboard.components.styling import color_team_table


def render(selected_season, seasons):
    st.header("🔍 Player Analysis")
    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------------------
    # Player selector
    # ------------------------------------------------------------
    players = run_query(
        "SELECT DISTINCT PLAYER_NAME FROM season_stats ORDER BY PLAYER_NAME"
    )
    player = st.selectbox("Select a Player", players["PLAYER_NAME"])

    if not player:
        st.warning("Please select a player.")
        return

    # ------------------------------------------------------------
    # Load player season stats
    # ------------------------------------------------------------
    df_player = run_query(
        """
        SELECT PLAYER_NAME, TEAM_ABBREVIATION, AGE, GP, MIN,
               PTS, REB, AST, STL, BLK, TOV,
               FG_PCT, FG3_PCT,
               FGA, FGM, FG3M, FTA,
               NBA_FANTASY_PTS
        FROM season_stats
        WHERE PLAYER_NAME = ?
        AND SEASON = ?
        """,
        (player, selected_season)
    )

    if df_player.empty:
        st.error(f"{player} has no stats in {selected_season}. Try a different season.")
        return

    # Add advanced metrics
    df_player = add_advanced_metrics(df_player)

    # Team colors
    team = df_player["TEAM_ABBREVIATION"].iloc[0]
    primary = get_primary(team)
    secondary = get_secondary(team)

    # ------------------------------------------------------------
    # Player Summary Table
    # ------------------------------------------------------------
    st.subheader("Player Summary")

    styled_player = color_team_table(df_player, primary, secondary)
    st.dataframe(styled_player, use_container_width=True)

    # ------------------------------------------------------------
    # View selector
    # ------------------------------------------------------------
    view = st.radio(
        "View type",
        ["Basic Stats", "Advanced Metrics"],
        horizontal=True
    )

    # ------------------------------------------------------------
    # Basic Stats Chart
    # ------------------------------------------------------------
    if view == "Basic Stats":
        stats = ["PTS", "REB", "AST", "STL", "BLK"]
        values = [df_player[s].iloc[0] for s in stats]

        st.subheader("Key Stats (Per Game)")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(stats, values, color=primary, edgecolor=secondary, linewidth=3)
        st.pyplot(fig)

    # ------------------------------------------------------------
    # Advanced Metrics Chart
    # ------------------------------------------------------------
    else:
        adv_stats = ["TS_PCT", "EFG_PCT", "AST_TOV"]
        available = [s for s in adv_stats if s in df_player.columns]
        values = [df_player[s].iloc[0] for s in available]

        st.subheader("Advanced Metrics")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(available, values, color=primary, edgecolor=secondary, linewidth=3)
        st.pyplot(fig)

        st.markdown("""
        **TS%** — True Shooting % (efficiency including threes + free throws)  
        **eFG%** — Effective FG % (adjusts FG% for 3‑point value)  
        **AST/TOV** — Assist‑to‑Turnover Ratio  
        """)
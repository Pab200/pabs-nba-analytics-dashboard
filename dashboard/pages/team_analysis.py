import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from src.db import run_query
from src.team_stats import get_team_season_stats
from src.colors import get_primary, get_secondary
from src.utils import is_accurate_data_season
from dashboard.components.styling import color_team_table


def render(selected_season, seasons):
    st.header("🏙️ Team Analysis")
    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------------------
    # Team selector
    # ------------------------------------------------------------
    teams = run_query(
        """
        SELECT DISTINCT TEAM_ABBREVIATION
        FROM season_stats
        WHERE TEAM_ABBREVIATION NOT IN ('2TM', '3TM', '4TM')
        ORDER BY TEAM_ABBREVIATION
        """
    )

    team = st.selectbox("Choose a team", teams["TEAM_ABBREVIATION"])

    # ------------------------------------------------------------
    # Team info (city, nickname, founded, etc.)
    # ------------------------------------------------------------
    team_info = run_query(
        """
        SELECT full_name, city, state, nickname, year_founded, year_closed
        FROM teams
        WHERE abbreviation = ?
        """,
        (team,)
    ).iloc[0]

    primary = get_primary(team)
    secondary = get_secondary(team)

    st.subheader("Team Information")

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**City:** {team_info['city']}")
        st.write(f"**State:** {team_info['state']}")

    with col2:
        st.write(f"**Nickname:** {team_info['nickname']}")
        st.write(f"**Year Founded:** {team_info['year_founded']}")
        st.write(f"**Year Closed:** {team_info['year_closed'] if team_info['year_closed'] else 'Active'}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------------------
    # Team Season Performance Summary
    # ------------------------------------------------------------
    st.subheader(f"Team Performance Summary ({selected_season})")

    if not is_accurate_data_season(selected_season):
        st.warning(
            f"⚠️ Opponent game logs begin in 2010–11. "
            f"Defensive Rating and Pace for {selected_season} use estimated formulas."
        )

    df_team_metrics = get_team_season_stats(team, selected_season)

    if not df_team_metrics.empty:
        metrics = df_team_metrics.iloc[0]

        m1, m2, m3, m4 = st.columns(4)

        ortg_val = f"{metrics['OFF_RATING']:.1f}" if pd.notnull(metrics['OFF_RATING']) else "N/A"
        drtg_val = f"{metrics['DEF_RATING']:.1f}" if pd.notnull(metrics['DEF_RATING']) else "N/A"
        pace_val = f"{metrics['PACE']:.1f}" if pd.notnull(metrics['PACE']) else "N/A"
        poss_val = f"{int(metrics['TEAM_POSS']):,}" if pd.notnull(metrics['TEAM_POSS']) else "N/A"

        with m1:
            st.metric("Offensive Rating", ortg_val)
        with m2:
            st.metric("Defensive Rating", drtg_val)
        with m3:
            st.metric("Pace", pace_val)
        with m4:
            st.metric("Est. Possessions", poss_val)

        st.markdown("<br><br>", unsafe_allow_html=True)

    # ------------------------------------------------------------
    # Team Season Player Stats Table
    # ------------------------------------------------------------
    st.subheader("Team Season Statistics")

    df_team = run_query(
        """
        SELECT PLAYER_NAME, PTS, REB, AST, FG_PCT
        FROM season_stats
        WHERE TEAM_ABBREVIATION = ?
        AND SEASON = ?
        """,
        (team, selected_season)
    )

    styled_df = color_team_table(df_team, primary, secondary)
    st.dataframe(styled_df, use_container_width=True)

    # ------------------------------------------------------------
    # Team Points Bar Chart
    # ------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df_team["PLAYER_NAME"], df_team["PTS"], edgecolor=secondary, linewidth=3, color=primary)
    ax.set_xticklabels(df_team["PLAYER_NAME"], rotation=45)
    st.pyplot(fig)

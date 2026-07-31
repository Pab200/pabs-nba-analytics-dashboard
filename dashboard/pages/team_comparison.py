import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from src.db import run_query
from src.team_stats import get_team_season_stats
from src.colors import get_primary, get_secondary
from src.utils import is_modern_season, is_accurate_data_season
from dashboard.components.styling import color_team_table


def render(selected_season, seasons):
    st.header("🏆 Team Comparison")
    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------------------
    # Cross-season toggle
    # ------------------------------------------------------------
    cross_year = st.checkbox("Compare teams from different years")

    # ------------------------------------------------------------
    # Session state initialization
    # ------------------------------------------------------------
    if "compare_teams" not in st.session_state:
        st.session_state.compare_teams = [
            {"team": None, "season": selected_season},
            {"team": None, "season": selected_season}
        ]

    # ------------------------------------------------------------
    # Team list
    # ------------------------------------------------------------
    teams = run_query(
        """
        SELECT DISTINCT TEAM_ABBREVIATION
        FROM season_stats
        WHERE TEAM_ABBREVIATION NOT IN ('2TM', '3TM', '4TM')
        ORDER BY TEAM_ABBREVIATION
        """
    )

    # Add team button
    if st.button("➕ Add Team"):
        st.session_state.compare_teams.append(
            {"team": None, "season": selected_season}
        )

    st.subheader("Select Teams to Compare")

    # ------------------------------------------------------------
    # Team selectors
    # ------------------------------------------------------------
    for idx, entry in enumerate(st.session_state.compare_teams):
        st.markdown(f"### Team {idx+1}")

        colA, colB = st.columns(2)

        with colA:
            entry["season"] = (
                st.selectbox(
                    f"Season (Team {idx+1})",
                    seasons["SEASON"],
                    key=f"team_season_{idx}"
                )
                if cross_year else selected_season
            )

        with colB:
            entry["team"] = st.selectbox(
                f"Team {idx+1}",
                teams["TEAM_ABBREVIATION"],
                key=f"team_{idx}"
            )

    # ------------------------------------------------------------
    # Load team stats
    # ------------------------------------------------------------
    team_dfs = []

    if any(not is_modern_season(e["season"]) for e in st.session_state.compare_teams):
        st.warning("⚠️ Defensive Rating is unavailable before 1996–97.")

    if any(not is_accurate_data_season(e["season"]) for e in st.session_state.compare_teams):
        st.warning("⚠️ Seasons before 2010–11 use estimated formulas for ORtg, DRtg, and Pace.")

    for entry in st.session_state.compare_teams:
        team = entry["team"]
        season = entry["season"]

        if team:
            df = get_team_season_stats(team, season)
            if df.empty:
                st.error(f"{team} has no stats in {season}.")
            else:
                team_dfs.append(df)

    if len(team_dfs) == 0:
        st.warning("Please select at least one valid team.")
        st.stop()

    # ------------------------------------------------------------
    # Team Summaries
    # ------------------------------------------------------------
    st.subheader("Team Summaries")

    for df in team_dfs:
        team = df["TEAM_ABBREVIATION"].iloc[0]
        primary = get_primary(team)
        secondary = get_secondary(team)

        # Replace NaN with None so JSON serialization won't crash
        clean_df = df.replace({np.nan: None})

        styled = color_team_table(clean_df, primary, secondary)
        st.dataframe(styled, use_container_width=True)

    # ------------------------------------------------------------
    # Comparison Table
    # ------------------------------------------------------------
    st.subheader("📊 Team Comparison Table")

    metrics = {
        "Offensive Rating": "OFF_RATING",
        "Defensive Rating": "DEF_RATING",
        "Pace": "PACE",
        "Rebounds": "TEAM_REB",
        "Assists": "TEAM_AST",
        "3PA": "TEAM_FG3A"
    }

    data = []
    for label, col in metrics.items():
        row = {"Metric": label}
        for df in team_dfs:
            team_name = df["TEAM_ABBREVIATION"].iloc[0]
            val = df[col].iloc[0] if col in df.columns else None
            
            # Explicitly check pd.notna(val) and avoid returning float NaN
            if val is not None and pd.notna(val):
                row[team_name] = round(float(val), 2)
            else:
                row[team_name] = None
                
        data.append(row)

    df_compare = pd.DataFrame(data)
    
    # Final check: Convert any remaining NaN to None for safety
    df_compare = df_compare.replace({np.nan: None})
    st.dataframe(df_compare, use_container_width=True)

    # ------------------------------------------------------------
    # Grouped Bar Charts
    # ------------------------------------------------------------
    names = [df["TEAM_ABBREVIATION"].iloc[0] for df in team_dfs]
    colors = [get_primary(name) for name in names]
    edges = [get_secondary(name) for name in names]

    # Core Metrics Chart
    st.subheader("📈 Core Metrics (ORtg, DRtg, Pace)")

    core_labels = ["OFF_RATING", "DEF_RATING", "PACE"]
    x = np.arange(len(core_labels))
    width = 0.8 / len(team_dfs)

    fig, ax = plt.subplots(figsize=(14, 6))
    for i, df in enumerate(team_dfs):
        # Convert NaN values to 0 for plotting so Matplotlib doesn't break
        vals = [df[label].iloc[0] if (label in df.columns and pd.notna(df[label].iloc[0])) else 0 for label in core_labels]
        ax.bar(
            x + (i - len(team_dfs) / 2) * width,
            vals,
            width,
            label=names[i],
            color=colors[i],
            edgecolor=edges[i],
            linewidth=3
        )

    ax.set_xticks(x)
    ax.set_xticklabels(["ORtg", "DRtg", "Pace"])
    ax.legend()
    st.pyplot(fig, use_container_width=True)

    # Counting Stats Chart
    st.subheader("📉 Counting Stats (REB, AST, 3PA)")

    count_labels = ["TEAM_REB", "TEAM_AST", "TEAM_FG3A"]
    x = np.arange(len(count_labels))

    fig, ax = plt.subplots(figsize=(14, 6))
    for i, df in enumerate(team_dfs):
        vals = [df[label].iloc[0] if (label in df.columns and pd.notna(df[label].iloc[0])) else 0 for label in count_labels]
        ax.bar(
            x + (i - len(team_dfs) / 2) * width,
            vals,
            width,
            label=names[i],
            color=colors[i],
            edgecolor=edges[i],
            linewidth=3
        )

    ax.set_xticks(x)
    ax.set_xticklabels(["REB", "AST", "3PA"])
    ax.legend()
    st.pyplot(fig, use_container_width=True)
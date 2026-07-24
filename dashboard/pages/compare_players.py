import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from src.db import run_query
from src.metrics import add_advanced_metrics
from src.colors import get_primary, get_secondary
from src.utils import is_modern_season, is_accurate_data_season
from dashboard.components.styling import color_team_table


def render(selected_season, seasons):
    st.header("🤝 Compare Players")
    st.markdown("<br>", unsafe_allow_html=True)

    # Allow cross-season comparison
    cross_year = st.checkbox("Compare players from different years")

    # Initialize session state
    if "compare_players" not in st.session_state:
        st.session_state.compare_players = [
            {"player": None, "season": selected_season},
            {"player": None, "season": selected_season}
        ]

    # Player list
    players = run_query("SELECT DISTINCT PLAYER_NAME FROM season_stats ORDER BY PLAYER_NAME")

    # Add player button
    if st.button("➕ Add Player"):
        st.session_state.compare_players.append(
            {"player": None, "season": selected_season}
        )

    st.subheader("Select Players to Compare")

    # Player selectors
    for idx, entry in enumerate(st.session_state.compare_players):
        st.markdown(f"### Player {idx+1}")

        colA, colB = st.columns(2)

        with colA:
            if cross_year:
                entry["season"] = st.selectbox(
                    f"Season (Player {idx+1})",
                    seasons["SEASON"],
                    key=f"season_{idx}"
                )
            else:
                entry["season"] = selected_season

        with colB:
            entry["player"] = st.selectbox(
                f"Player {idx+1}",
                players["PLAYER_NAME"],
                key=f"player_{idx}"
            )

    # ------------------------------------------------------------
    # Load player stats
    # ------------------------------------------------------------
    def get_player_season_stats(player_name, season):
        df = run_query(
            """
            SELECT PLAYER_NAME, TEAM_ABBREVIATION, AGE, GP, MIN,
                   PTS, REB, AST, STL, BLK, TOV,
                   FGM, FGA, FG_PCT,
                   FG3M, FG3A, FG3_PCT,
                   FTM, FTA, FT_PCT,
                   NBA_FANTASY_PTS
            FROM season_stats
            WHERE PLAYER_NAME = ?
            AND SEASON = ?
            """,
            (player_name, season)
        )
        if not df.empty:
            df = add_advanced_metrics(df)
        return df

    player_dfs = []
    valid_players = []

    for entry in st.session_state.compare_players:
        player = entry["player"]
        season = entry["season"]

        if player:
            df = get_player_season_stats(player, season)
            if df.empty:
                st.error(f"{player} has no stats in {season}.")
            else:
                player_dfs.append(df)
                valid_players.append(player)

    if len(player_dfs) == 0:
        st.warning("Please select at least one valid player.")
        st.stop()

    # ------------------------------------------------------------
    # Player Summaries
    # ------------------------------------------------------------
    st.subheader("Player Summaries")

    for df in player_dfs:
        team = df["TEAM_ABBREVIATION"].iloc[0]
        primary = get_primary(team)
        secondary = get_secondary(team)

        styled = color_team_table(df, primary, secondary)
        st.dataframe(styled, use_container_width=True)

    # ------------------------------------------------------------
    # Comparison Table
    # ------------------------------------------------------------
    st.subheader("📊 Player Comparison Table")

    metrics = {
        "Points (PTS)": "PTS",
        "Assists (AST)": "AST",
        "Rebounds (REB)": "REB",
        "Steals (STL)": "STL",
        "Blocks (BLK)": "BLK",
        "True Shooting % (TS%)": "TS_PCT",
        "Effective FG % (eFG%)": "EFG_PCT",
        "FG%": "FG_PCT",
        "3P%": "FG3_PCT",
        "FT%": "FT_PCT",
    }

    data = []
    for label, col in metrics.items():
        row = {"Metric": label}
        for df in player_dfs:
            name = df["PLAYER_NAME"].iloc[0]
            val = df[col].iloc[0] if col in df.columns else None
            row[name] = round(val, 3) if pd.notna(val) else None
        data.append(row)

    df_compare = pd.DataFrame(data)
    st.dataframe(df_compare, use_container_width=True)

    # ------------------------------------------------------------
    # Per-Game Stats Chart
    # ------------------------------------------------------------
    st.subheader("📈 Per-Game Stats Comparison")

    per_game_metrics = ["PTS", "REB", "AST", "STL", "BLK"]
    x = np.arange(len(per_game_metrics))
    width = 0.8 / len(player_dfs)

    fig, ax = plt.subplots(figsize=(12, 6))

    for i, df in enumerate(player_dfs):
        name = df["PLAYER_NAME"].iloc[0]
        team = df["TEAM_ABBREVIATION"].iloc[0]
        primary = get_primary(team)
        secondary = get_secondary(team)

        vals = [df[m].iloc[0] if m in df.columns else 0 for m in per_game_metrics]

        ax.bar(x + (i - len(player_dfs)/2)*width, vals, width,
               label=name, color=primary, edgecolor=secondary, linewidth=3)

    ax.set_xticks(x)
    ax.set_xticklabels(per_game_metrics)
    ax.legend()
    st.pyplot(fig, use_container_width=True)

    # ------------------------------------------------------------
    # Shooting & Efficiency Chart
    # ------------------------------------------------------------
    st.subheader("📉 Shooting & Efficiency Comparison")

    pct_metrics = ["TS_PCT", "EFG_PCT", "FG_PCT", "FG3_PCT", "FT_PCT"]
    pct_labels = ["TS%", "eFG%", "FG%", "3P%", "FT%"]

    x = np.arange(len(pct_labels))

    fig, ax = plt.subplots(figsize=(12, 6))

    for i, df in enumerate(player_dfs):
        name = df["PLAYER_NAME"].iloc[0]
        team = df["TEAM_ABBREVIATION"].iloc[0]
        primary = get_primary(team)
        secondary = get_secondary(team)

        vals = [df[m].iloc[0] if m in df.columns else 0 for m in pct_metrics]

        ax.bar(x + (i - len(player_dfs)/2)*width, vals, width,
               label=name, color=primary, edgecolor=secondary, linewidth=3)

    ax.set_xticks(x)
    ax.set_xticklabels(pct_labels)
    ax.legend()
    st.pyplot(fig, use_container_width=True)

    st.markdown("""
    **TS%**: Scoring efficiency including threes and free throws.  
    **eFG%**: FG% adjusted for the extra value of 3s.  
    Shooting splits show FG%, 3P%, and FT% side by side.
    """)
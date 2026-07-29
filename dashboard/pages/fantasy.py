# dashboard/pages/fantasy.py

import os
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from src.colors import get_primary, get_secondary
from src.db import run_query
from src.fantasy.boom_bust import analyze_boom_bust
from src.fantasy.consistency import analyze_player_consistency
from src.fantasy.scoring import DEFAULT_SCORING, add_fantasy_scores


# ------------------------------------------------------------
# MAIN PAGE
# ------------------------------------------------------------
def render(selected_season, seasons):
    st.header("🪄 Fantasy Analytics Center")
    st.markdown("<br>", unsafe_allow_html=True)

    tab_leaderboard, tab_consistency, tab_boom_bust = st.tabs([
        "Leaderboard",
        "Consistency",
        "Boom/Bust"
    ])

    with tab_leaderboard:
        render_leaderboard(selected_season)

    with tab_consistency:
        render_consistency(selected_season)

    with tab_boom_bust:
        render_boom_bust(selected_season)


# ------------------------------------------------------------
# LEADERBOARD TAB
# ------------------------------------------------------------
def render_leaderboard(selected_season):

    df = run_query(
        """
        SELECT PLAYER_NAME, TEAM_ABBREVIATION, GP,
               PTS, REB, AST, STL, BLK, TOV
        FROM season_stats
        WHERE SEASON = ?
        """,
        (selected_season,)
    )

    if df.empty:
        st.error("No data available for this season")
        return

    st.subheader("⚙️ Custom Scoring Settings")

    scoring = {}
    for stat, default in DEFAULT_SCORING.items():
        scoring[stat] = st.number_input(
            f"{stat} weight",
            value=float(default),
            step=0.1,
            key=f"lb_fantasy_weight_{stat}"
        )

    df = add_fantasy_scores(df, scoring)

    metric = st.radio(
        "Fantasy metric",
        ["Fantasy Points Per Game", "Total Fantasy Points"],
        horizontal=True
    )

    y_col = "FANTASY_PPG" if metric == "Fantasy Points Per Game" else "FANTASY_TOTAL"

    top_n = st.slider("Show Top N Players", 10, 100, 25)

    df_ranked = df.sort_values(y_col, ascending=False).head(top_n)

    prim = [get_primary(t) for t in df_ranked["TEAM_ABBREVIATION"]]
    sec = [get_secondary(t) for t in df_ranked["TEAM_ABBREVIATION"]]

    st.subheader(f"Top {top_n} - {metric}")

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.bar(df_ranked["PLAYER_NAME"], df_ranked[y_col], color=prim, edgecolor=sec, linewidth=3)
    ax.set_xticks(range(len(df_ranked)))
    ax.set_xticklabels(df_ranked["PLAYER_NAME"], rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)

    st.subheader("Leaderboard Table")

    def style_team_rows(row):
        team = row["TEAM_ABBREVIATION"]
        p_color = get_primary(team)
        s_color = get_secondary(team)
        return [f"background-color: {s_color}30; color: {p_color}; border: 1px solid {p_color};" for _ in row]

    styled = df_ranked.style.apply(style_team_rows, axis=1)
    st.dataframe(styled, use_container_width=True)


# ------------------------------------------------------------
# CONSISTENCY TAB
# ------------------------------------------------------------
def render_consistency(selected_season):

    file_path = f"data/player_game_logs/{selected_season}/player_game_logs{selected_season}.csv"

    if not os.path.exists(file_path):
        st.error("Game logs not downloaded for this season.")
        return

    df_players = pd.read_csv(file_path)
    players = sorted(df_players["PLAYER_NAME"].unique())

    st.subheader("Select Player")
    player = st.selectbox("Player", players, key="cons_player_select")

    if not player:
        return

    df_player = df_players[df_players["PLAYER_NAME"] == player].copy()

    st.subheader("⚙️ Custom Scoring")

    scoring = {}
    for stat, default in DEFAULT_SCORING.items():
        scoring[stat] = st.number_input(
            f"{stat} weight", 
            value=float(default), 
            step=0.1, 
            key=f"cons_fantasy_weight_{stat}"
        )

    df_with_fp, metrics = analyze_player_consistency(df_player, scoring)

    st.subheader("📊 Consistency Summary")
    st.write(f"**Fantasy PPG:** {metrics['mean_fp']:.2f}")
    st.write(f"**Standard Deviation:** {metrics['std_fp']:.2f}")
    st.write(f"**Coefficient of Variation:** {metrics['cv_fp']:.2f}")
    st.write(f"**Classification:** {metrics['label']}")

    st.subheader("📈 Fantasy Points Per Game")

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df_with_fp["FANTASY_PTS"], marker="o")
    ax.set_title(f"{player} - Fantasy Points Per Game")
    ax.set_xlabel("Game Number")
    ax.set_ylabel("Fantasy Points")
    st.pyplot(fig)

    st.subheader("Game Log Table")
    st.dataframe(df_with_fp, use_container_width=True)


# ------------------------------------------------------------
# BOOM/BUST TAB
# ------------------------------------------------------------
def render_boom_bust(selected_season):

    # ------------------------------------------------------------
    # Load game logs
    # ------------------------------------------------------------
    file_path = f"data/player_game_logs/{selected_season}/player_game_logs{selected_season}.csv"

    if not os.path.exists(file_path):
        st.error("Game logs not downloaded for this season.")
        return

    df_logs = pd.read_csv(file_path)
    players = sorted(df_logs["PLAYER_NAME"].unique())

    # ------------------------------------------------------------
    # Player selector
    # ------------------------------------------------------------
    st.subheader("Select Player")
    player = st.selectbox("Player", players, key="bb_player_select")

    if not player:
        return

    df_player = df_logs[df_logs["PLAYER_NAME"] == player].copy()

    # ------------------------------------------------------------
    # Custom Scoring
    # ------------------------------------------------------------
    st.subheader("⚙️ Custom Scoring")

    scoring = {}
    for stat, default in DEFAULT_SCORING.items():
        scoring[stat] = st.number_input(
            f"{stat} weight", 
            value=float(default), 
            step=0.1, 
            key=f"bb_fantasy_weight_{stat}"
        )

    # Add fantasy points to game logs
    df_player["FANTASY_PTS"] = (
        df_player["PTS"] * scoring.get("PTS", 0)
        + df_player["REB"] * scoring.get("REB", 0)
        + df_player["AST"] * scoring.get("AST", 0)
        + df_player["STL"] * scoring.get("STL", 0)
        + df_player["BLK"] * scoring.get("BLK", 0)
        + df_player["TOV"] * scoring.get("TOV", 0)
    )

    # ------------------------------------------------------------
    # Boom/Bust analysis
    # ------------------------------------------------------------
    df_bb, metrics = analyze_boom_bust(df_player)

    boom_rate = metrics["boom_rate"]
    bust_rate = metrics["bust_rate"]
    neutral_rate = metrics["neutral_rate"]
    boom_threshold = metrics["boom_threshold"]
    bust_threshold = metrics.get("bust_threshold", metrics.get("bust_treshold", 0))

    mean_min = metrics["mean_minutes"]
    reliability = metrics["minutes_reliability"]
    classification = metrics["classification"]

    # ------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------
    st.subheader("📊 Boom/Bust Summary")

    st.write(f"**Boom Threshold (80th percentile):** {boom_threshold:.2f}")
    st.write(f"**Bust Threshold (20th percentile):** {bust_threshold:.2f}")
    st.write(f"**Boom Rate:** {boom_rate:.2%}")
    st.write(f"**Bust Rate:** {bust_rate:.2%}")
    st.write(f"**Neutral Rate:** {neutral_rate:.2%}")

    st.markdown("---")

    st.write(f"**Average Minutes:** {mean_min:.1f}")
    st.write(f"**Minutes Reliability Score:** {reliability:.2f}")
    st.write(f"**Final Classification:** {classification}")

    # ------------------------------------------------------------
    # Chart
    # ------------------------------------------------------------
    st.subheader("📈 Boom/Bust Chart")

    colors = df_bb["RESULT"].map({
        "Boom": "#4CAF50",      # green
        "Bust": "#F44336",      # red
        "Neutral": "#9E9E9E",   # gray
    })

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(range(len(df_bb)), df_bb["FANTASY_PTS"], color=colors)
    ax.set_title(f"{player} - Boom/Bust Breakdown")
    ax.set_xlabel("Game Number")
    ax.set_ylabel("Fantasy Points")
    st.pyplot(fig)

    # ------------------------------------------------------------
    # Table
    # ------------------------------------------------------------
    st.subheader("Boom/Bust Game Log")
    st.dataframe(df_bb, use_container_width=True)
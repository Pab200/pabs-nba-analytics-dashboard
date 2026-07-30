# dashboard/pages/fantasy.py

import os
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from src.colors import get_primary, get_secondary
from src.db import run_query
from src.fantasy.boom_bust import analyze_boom_bust
from src.fantasy.consistency import analyze_player_consistency
from src.fantasy.draft import analyze_player_draft
from src.fantasy.scoring import DEFAULT_SCORING, add_fantasy_scores
from src.fantasy.sleepers import analyze_player_sleeper
from src.fantasy.waiver import analyze_player_waiver


# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------
def _get_team_abbr(df_or_row):
    """Safely extracts team abbreviation across different CSV schemas."""
    cols = df_or_row.index if isinstance(df_or_row, pd.Series) else df_or_row.columns
    
    for c in ["TEAM_ABBREVIATION", "TEAM", "TEAM_ABBREVIATION_A"]:
        if c in cols:
            val = df_or_row[c]
            return val.iloc[0] if isinstance(val, pd.Series) else val

    if "MATCHUP" in cols:
        val = df_or_row["MATCHUP"]
        matchup_str = str(val.iloc[0] if isinstance(val, pd.Series) else val)
        return matchup_str.split()[0] if matchup_str else "N/A"

    return "N/A"


def _style_team_rows(row):
    """Applies primary and secondary team color styling to Streamlit dataframe rows."""
    team = _get_team_abbr(row)
    p_color = get_primary(team)
    s_color = get_secondary(team)
    return [f"background-color: {s_color}30; color: {p_color}; border: 1px solid {p_color};" for _ in row]


@st.cache_data
def _load_game_logs(file_path):
    """Cached loader for game logs."""
    if not os.path.exists(file_path):
        return None
    return pd.read_csv(file_path)


def _compute_fantasy_points(df, scoring):
    """Calculates fantasy points for game log DataFrames."""
    return (
        df["PTS"] * scoring.get("PTS", 0)
        + df["REB"] * scoring.get("REB", 0)
        + df["AST"] * scoring.get("AST", 0)
        + df["STL"] * scoring.get("STL", 0)
        + df["BLK"] * scoring.get("BLK", 0)
        + df["TOV"] * scoring.get("TOV", 0)
    )


# ------------------------------------------------------------
# MAIN PAGE
# ------------------------------------------------------------
def render(selected_season, seasons):
    st.header("🪄 Fantasy Analytics Center")
    st.markdown("<br>", unsafe_allow_html=True)

    tab_leaderboard, tab_consistency, tab_boom_bust, tab_sleepers, tab_waiver, tab_draft = st.tabs([
        "Leaderboard",
        "Consistency",
        "Boom/Bust",
        "Sleepers",
        "Waiver Wire",
        "Draft Board"
    ])

    with tab_leaderboard:
        render_leaderboard(selected_season)

    with tab_consistency:
        render_consistency(selected_season)

    with tab_boom_bust:
        render_boom_bust(selected_season)

    with tab_sleepers:
        render_sleepers(selected_season)

    with tab_waiver:
        render_waiver(selected_season)

    with tab_draft:
        render_draft(selected_season)


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
        horizontal=True,
        key="lb_metric_radio"
    )

    y_col = "FANTASY_PPG" if metric == "Fantasy Points Per Game" else "FANTASY_TOTAL"

    top_n = st.slider("Show Top N Players", 10, 100, 25, key="lb_top_n_slider")

    df_ranked = df.sort_values(y_col, ascending=False).head(top_n)

    prim = [get_primary(_get_team_abbr(row)) for _, row in df_ranked.iterrows()]
    sec = [get_secondary(_get_team_abbr(row)) for _, row in df_ranked.iterrows()]

    st.subheader(f"Top {top_n} - {metric}")

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.bar(df_ranked["PLAYER_NAME"], df_ranked[y_col], color=prim, edgecolor=sec, linewidth=3)
    ax.set_xticks(range(len(df_ranked)))
    ax.set_xticklabels(df_ranked["PLAYER_NAME"], rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)

    st.subheader("Leaderboard Table")
    styled = df_ranked.style.apply(_style_team_rows, axis=1)
    st.dataframe(styled, use_container_width=True)


# ------------------------------------------------------------
# CONSISTENCY TAB
# ------------------------------------------------------------
def render_consistency(selected_season):

    file_path = f"data/player_game_logs/{selected_season}/player_game_logs{selected_season}.csv"
    df_players = _load_game_logs(file_path)

    if df_players is None:
        st.error("Game logs not downloaded for this season.")
        return

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

    file_path = f"data/player_game_logs/{selected_season}/player_game_logs{selected_season}.csv"
    df_logs = _load_game_logs(file_path)

    if df_logs is None:
        st.error("Game logs not downloaded for this season.")
        return

    players = sorted(df_logs["PLAYER_NAME"].unique())

    st.subheader("Select Player")
    player = st.selectbox("Player", players, key="bb_player_select")

    if not player:
        return

    df_player = df_logs[df_logs["PLAYER_NAME"] == player].copy()

    st.subheader("⚙️ Custom Scoring")

    scoring = {}
    for stat, default in DEFAULT_SCORING.items():
        scoring[stat] = st.number_input(
            f"{stat} weight", 
            value=float(default), 
            step=0.1, 
            key=f"bb_fantasy_weight_{stat}"
        )

    df_player["FANTASY_PTS"] = _compute_fantasy_points(df_player, scoring)

    df_bb, metrics = analyze_boom_bust(df_player)

    boom_rate = metrics["boom_rate"]
    bust_rate = metrics["bust_rate"]
    neutral_rate = metrics["neutral_rate"]
    boom_threshold = metrics["boom_threshold"]
    bust_threshold = metrics.get("bust_threshold", metrics.get("bust_treshold", 0))

    mean_min = metrics["mean_minutes"]
    reliability = metrics["minutes_reliability"]
    classification = metrics["classification"]

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

    st.subheader("Boom/Bust Game Log")
    st.dataframe(df_bb, use_container_width=True)


# ------------------------------------------------------------
# SLEEPERS TAB
# ------------------------------------------------------------
def render_sleepers(selected_season):

    file_path = f"data/player_game_logs/{selected_season}/player_game_logs{selected_season}.csv"
    df_logs = _load_game_logs(file_path)

    if df_logs is None:
        st.error("Game logs not downloaded for this season.")
        return

    st.subheader("⚙️ Custom Scoring")
    scoring = {}
    for stat, default in DEFAULT_SCORING.items():
        scoring[stat] = st.number_input(
            f"{stat} weight", 
            value=float(default), 
            step=0.1,
            key=f"sleeper_fantasy_weight_{stat}"
        )

    df_logs["FANTASY_PTS"] = _compute_fantasy_points(df_logs, scoring)

    sleeper_rows = []

    for player in sorted(df_logs["PLAYER_NAME"].unique()):
        df_player = df_logs[df_logs["PLAYER_NAME"] == player]

        if len(df_player) < 5:
            continue

        metrics = analyze_player_sleeper(df_player)

        sleeper_rows.append({
            "PLAYER_NAME": player,
            "TEAM_ABBREVIATION": _get_team_abbr(df_player),
            "SLEEPER_SCORE": metrics["sleeper_score"],
            "BREAKOUT_PROB": metrics["breakout_prob"],
            "BOOM_RATE": metrics["boom_rate"],
            "BUST_RATE": metrics["bust_rate"],
            "RELIABILITY": metrics["reliability"],
            "TREND_SCORE": metrics["trend_score"],
            "CLASSIFICATION": metrics["classification"]
        })

    df_sleeper = pd.DataFrame(sleeper_rows)

    if df_sleeper.empty:
        st.warning("No sleeper candidates found for this season.")
        return

    df_sleeper = df_sleeper.sort_values("SLEEPER_SCORE", ascending=False)

    st.subheader("🌟 Top Sleeper Candidates")

    top_n = st.slider("Show Top N Sleepers", 5, 50, 15, key="sleeper_top_n_slider")

    df_top = df_sleeper.head(top_n)

    prim = [get_primary(_get_team_abbr(row)) for _, row in df_top.iterrows()]
    sec = [get_secondary(_get_team_abbr(row)) for _, row in df_top.iterrows()]

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.bar(df_top["PLAYER_NAME"], df_top["SLEEPER_SCORE"], color=prim, edgecolor=sec, linewidth=3)
    ax.set_xticks(range(len(df_top)))
    ax.set_xticklabels(df_top["PLAYER_NAME"], rotation=45, ha='right')
    ax.set_title("Top Sleeper Scores")
    ax.set_ylabel("Sleeper Score")
    plt.tight_layout()
    st.pyplot(fig)

    st.subheader("Sleeper Leaderboard")
    styled = df_top.style.apply(_style_team_rows, axis=1)
    st.dataframe(styled, use_container_width=True)


# ------------------------------------------------------------
# WAIVER WIRE TAB
# ------------------------------------------------------------
def render_waiver(selected_season):

    file_path = f"data/player_game_logs/{selected_season}/player_game_logs{selected_season}.csv"
    df_logs = _load_game_logs(file_path)

    if df_logs is None:
        st.error("Game logs not downloaded for this season.")
        return

    st.subheader("⚙️ Custom Scoring")

    scoring = {}
    for stat, default in DEFAULT_SCORING.items():
        scoring[stat] = st.number_input(
            f"{stat} weight", 
            value=float(default), 
            step=0.1,
            key=f"waiver_fantasy_weight_{stat}"
        )

    df_logs["FANTASY_PTS"] = _compute_fantasy_points(df_logs, scoring)

    waiver_rows = []

    for player in sorted(df_logs["PLAYER_NAME"].unique()):
        df_player = df_logs[df_logs["PLAYER_NAME"] == player]

        if len(df_player) < 5:
            continue

        metrics = analyze_player_waiver(df_player)

        waiver_rows.append({
            "PLAYER_NAME": player,
            "TEAM_ABBREVIATION": _get_team_abbr(df_player),
            "WAIVER_SCORE": metrics["waiver_score"],
            "AVAILABILITY": metrics["availability"],
            "OPPORTUNITY": metrics["opportunity"],
            "BOOM_RATE": metrics["boom_rate"],
            "BUST_RATE": metrics["bust_rate"],
            "RELIABILITY": metrics["reliability"],
            "TREND_SCORE": metrics["trend_score"],
            "BREAKOUT_PROB": metrics["breakout_prob"],
            "CLASSIFICATION": metrics["classification"]
        })

    df_waiver = pd.DataFrame(waiver_rows)

    if df_waiver.empty:
        st.warning("No waiver wire candidates found.")
        return

    df_waiver = df_waiver.sort_values("WAIVER_SCORE", ascending=False)

    st.subheader("🔥 Top Waiver Wire Targets")

    top_n = st.slider("Show Top N Waiver Targets", 5, 50, 15, key="waiver_top_n_slider")

    df_top = df_waiver.head(top_n)

    prim = [get_primary(_get_team_abbr(row)) for _, row in df_top.iterrows()]
    sec = [get_secondary(_get_team_abbr(row)) for _, row in df_top.iterrows()]

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.bar(df_top["PLAYER_NAME"], df_top["WAIVER_SCORE"], color=prim, edgecolor=sec, linewidth=3)
    ax.set_xticks(range(len(df_top)))
    ax.set_xticklabels(df_top["PLAYER_NAME"], rotation=45, ha='right')
    ax.set_title("Top Waiver Wire Scores")
    ax.set_ylabel("Waiver Score")
    plt.tight_layout()
    st.pyplot(fig)

    st.subheader("Waiver Wire Leaderboard")
    styled = df_top.style.apply(_style_team_rows, axis=1)
    st.dataframe(styled, use_container_width=True)


# ------------------------------------------------------------
# ⭐ DRAFT BOARD TAB (FINAL ENHANCED VERSION)
# ------------------------------------------------------------
def render_draft(selected_season):

    file_path = f"data/player_game_logs/{selected_season}/player_game_logs{selected_season}.csv"
    df_logs = _load_game_logs(file_path)

    if df_logs is None:
        st.error("Game logs not downloaded for this season.")
        return

    # Optional: Position filter (only if POSITION column exists)
    if "POSITION" in df_logs.columns:
        pos = st.multiselect(
            "Filter by Position",
            sorted(df_logs["POSITION"].unique()),
            default=None
        )
        if pos:
            df_logs = df_logs[df_logs["POSITION"].isin(pos)]

    st.subheader("⚙️ Custom Scoring")

    scoring = {}
    for stat, default in DEFAULT_SCORING.items():
        scoring[stat] = st.number_input(
            f"{stat} weight",
            value=float(default),
            step=0.1,
            key=f"draft_fantasy_weight_{stat}"
        )

    # Calculate fantasy points once
    df_logs["FANTASY_PTS"] = _compute_fantasy_points(df_logs, scoring)

    draft_rows = []

    for player in sorted(df_logs["PLAYER_NAME"].unique()):
        df_player = df_logs[df_logs["PLAYER_NAME"] == player]

        if len(df_player) < 5:
            continue

        metrics = analyze_player_draft(df_player, scoring)

        draft_rows.append({
            "PLAYER_NAME": player,
            "TEAM_ABBREVIATION": _get_team_abbr(df_player),
            "DRAFT_SCORE": metrics["draft_score"],
            "TIER": metrics["tier"],
            "RISK": metrics["risk"],
            "ROLE": metrics["role"],
            "FANTASY_PPG": metrics["fp_ppg"],
            "BOOM_RATE": metrics["boom_rate"],
            "BUST_RATE": metrics["bust_rate"],
            "RELIABILITY": metrics["reliability"]
        })

    df_draft = pd.DataFrame(draft_rows)

    if df_draft.empty:
        st.warning("No draft candidates found.")
        return

    df_draft = df_draft.sort_values("DRAFT_SCORE", ascending=False)

    st.subheader("🏆 Draft Board (Tier System)")

    # Tier summary
    tier_counts = df_draft["TIER"].value_counts().to_dict()
    st.markdown(f"""
### Tier Summary  
- 🟡 **S Tier:** {tier_counts.get('S', 0)}  
- 🔵 **A Tier:** {tier_counts.get('A', 0)}  
- 🟢 **B Tier:** {tier_counts.get('B', 0)}  
- 🟠 **C Tier:** {tier_counts.get('C', 0)}  
- 🔴 **D Tier:** {tier_counts.get('D', 0)}
""")

    # Range slider: lets you browse ANY part of the draft board
    start, end = st.slider(
        "Select Draft Board Range (by rank)",
        min_value=1,
        max_value=len(df_draft),
        value=(1, 25),
        step=1,
        key="draft_range_slider"
    )

    # Slice the sorted draft board
    df_top = df_draft.iloc[start-1:end]


    # Role icons
    role_icons = {
        "Full-Time Starter": "⭐",
        "Strong Rotation": "🔵",
        "Bench Contributor": "🟢",
        "Fringe Rotation": "⚪",
    }
    df_top["ROLE_ICON"] = df_top["ROLE"].map(role_icons)

    # Team colors
    prim = [get_primary(_get_team_abbr(row)) for _, row in df_top.iterrows()]
    sec = [get_secondary(_get_team_abbr(row)) for _, row in df_top.iterrows()]

    # Tier colors for chart
    tier_colors = {
        "S": "#FFD700",
        "A": "#1E90FF",
        "B": "#32CD32",
        "C": "#FFA500",
        "D": "#FF4500",
    }
    bar_colors = [tier_colors[t] for t in df_top["TIER"]]

    # Chart
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.bar(df_top["PLAYER_NAME"], df_top["DRAFT_SCORE"], color=bar_colors, edgecolor=sec, linewidth=3)
    ax.set_xticks(range(len(df_top)))
    ax.set_xticklabels(df_top["PLAYER_NAME"], rotation=45, ha='right')
    ax.set_title("Draft Score Rankings")
    ax.set_ylabel("Draft Score")
    plt.tight_layout()
    st.pyplot(fig)

    # Table with tier + risk borders
    st.subheader("Draft Board Table")

    def _style_draft_rows(row):
        tier = row["TIER"]
        risk = row["RISK"]
        team = _get_team_abbr(row)

        # Team colors
        p_color = get_primary(team)
        s_color = get_secondary(team)

        # Tier colors
        tier_colors = {
            "S": "#FFD700",
            "A": "#1E90FF",
            "B": "#32CD32",
            "C": "#FFA500",
            "D": "#FF4500",
        }
        t_color = tier_colors.get(tier, "#FFFFFF")

        # Risk colors
        risk_colors = {
            "Low": "#4CAF50",
            "Medium": "#FFC107",
            "High": "#F44336",
        }
        r_color = risk_colors.get(risk, "#FFFFFF")

        return [
            f"background-color: {s_color}30; color: {p_color}; "
            f"border-left: 6px solid {t_color}; border-right: 6px solid {r_color};"
            for _ in row
        ]

    # Display table with role icons included
    df_display = df_top[[
        "PLAYER_NAME", "TEAM_ABBREVIATION", "ROLE_ICON", "TIER",
        "DRAFT_SCORE", "RISK", "FANTASY_PPG", "BOOM_RATE", "BUST_RATE", "RELIABILITY"
    ]]

    styled = df_display.style.apply(_style_draft_rows, axis=1)
    st.dataframe(styled, use_container_width=True)
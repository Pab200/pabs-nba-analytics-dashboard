import streamlit as st
import pandas as pd
from pathlib import Path

from src.shot_charts.fetch_data import get_player_shots
from src.shot_charts.process import prepare_for_plotting
from src.shot_charts.plotting import plot_shots
from src.shot_charts.heatmap import plot_heatmap
from src.shot_charts.hexbin import plot_hexbin
import src.shot_charts.filters as shot_filters


# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"


def load_season_stats_csv(season: str) -> pd.DataFrame:
    return pd.read_csv(RAW_DIR / f"season_stats_{season}.csv")


def load_team_game_stats_csv(season: str) -> pd.DataFrame:
    path = RAW_DIR / f"team_game_stats_{season}.csv"
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


# ------------------------------------------------------------
# Player selector
# ------------------------------------------------------------

def build_player_selector(df_stats: pd.DataFrame):
    players = df_stats[["PLAYER_ID", "PLAYER_NAME", "TEAM_ABBREVIATION"]].drop_duplicates()
    players["display"] = players["PLAYER_NAME"] + " (" + players["TEAM_ABBREVIATION"] + ")"

    choice = st.selectbox("Player", players["display"])
    row = players[players["display"] == choice].iloc[0]

    return int(row["PLAYER_ID"]), row["PLAYER_NAME"], row["TEAM_ABBREVIATION"]


# ------------------------------------------------------------
# Filters
# ------------------------------------------------------------

def apply_simple_filters(df: pd.DataFrame):
    st.subheader("Filters")

    zones_basic = sorted(df["SHOT_ZONE_BASIC"].dropna().unique())
    zone_basic = st.selectbox("Zone (basic)", ["All"] + zones_basic)

    shot_types = sorted(df["SHOT_TYPE"].dropna().unique())
    shot_type = st.selectbox("Shot Type", ["All"] + shot_types)

    made_filter = st.selectbox("Result", ["All", "Made", "Missed"])

    periods = sorted(df["PERIOD"].dropna().unique())
    period = st.selectbox("Period", ["All"] + [int(p) for p in periods])

    min_dist, max_dist = float(df["SHOT_DISTANCE"].min()), float(df["SHOT_DISTANCE"].max())
    dist_range = st.slider(
        "Shot Distance Range (ft)",
        min_value=int(min_dist),
        max_value=int(max_dist),
        value=(int(min_dist), int(max_dist))
    )

    out = df.copy()

    if zone_basic != "All":
        out = shot_filters.filter_zone_basic(out, zone_basic)

    if shot_type != "All":
        out = shot_filters.filter_shot_type(out, shot_type)

    if made_filter == "Made":
        out = shot_filters.filter_made(out)
    elif made_filter == "Missed":
        out = shot_filters.filter_missed(out)

    if period != "All":
        out = shot_filters.filter_period(out, period)

    out = shot_filters.filter_distance_range(out, dist_range[0], dist_range[1])

    return out


# ------------------------------------------------------------
# Hover enrichment with game info
# ------------------------------------------------------------

def enrich_hover_with_game_info(df_shots: pd.DataFrame, df_games: pd.DataFrame) -> pd.DataFrame:
    if df_games.empty or "GAME_ID" not in df_games.columns:
        return df_shots

    df_shots["GAME_ID"] = pd.to_numeric(df_shots["GAME_ID"], errors="coerce").astype("Int64").astype(str)
    df_games["GAME_ID"] = pd.to_numeric(df_games["GAME_ID"], errors="coerce").astype("Int64").astype(str)
    df_games = df_games[df_games["GAME_ID"].notna()]

    merged = df_shots.merge(df_games, on="GAME_ID", how="left", suffixes=("", "_GAME"))

    def build_hover(r):
        base = (
            f"{r['SHOT_TYPE']} • {r['SHOT_DISTANCE']} ft"
            f"<br>{r['SHOT_ZONE_BASIC']} • {r['SHOT_ZONE_RANGE']}"
            f"<br>Q{int(r['PERIOD'])}"
        )

        matchup = r.get("MATCHUP", "")
        wl = r.get("WL", "")
        pts = r.get("PTS", "")
        fgm = r.get("FGM", "")
        fga = r.get("FGA", "")
        fg_pct = r.get("FG_PCT", "")
        date = r.get("GAME_DATE", "")
        game_id = r.get("GAME_ID", "")

        game_info = (
            f"<br>{matchup} • {wl} • {pts} pts"
            f"<br>FG: {fgm}/{fga} ({fg_pct})"
            f"<br>{date} • Game ID: {game_id}"
        )

        return base + game_info

    merged["hover"] = merged.apply(build_hover, axis=1)
    merged["color"] = merged["SHOT_MADE_FLAG"].map({1: "green", 0: "red"})

    return merged


# ------------------------------------------------------------
# Season stats summary
# ------------------------------------------------------------

def compute_season_stats(df: pd.DataFrame):
    total = len(df)
    made = int(df["SHOT_MADE_FLAG"].sum())
    missed = total - made
    fg_pct = made / total * 100 if total > 0 else 0.0

    by_type = (
        df.groupby("SHOT_TYPE")["SHOT_MADE_FLAG"]
        .agg(["sum", "count"])
        .rename(columns={"sum": "made", "count": "attempts"})
    )
    by_type["missed"] = by_type["attempts"] - by_type["made"]
    by_type["fg_pct"] = by_type["made"] / by_type["attempts"] * 100

    by_zone = (
        df.groupby("SHOT_ZONE_BASIC")["SHOT_MADE_FLAG"]
        .agg(["sum", "count"])
        .rename(columns={"sum": "made", "count": "attempts"})
    )
    by_zone["missed"] = by_zone["attempts"] - by_zone["made"]
    by_zone["fg_pct"] = by_zone["made"] / by_zone["attempts"] * 100

    return total, made, missed, fg_pct, by_type, by_zone


# ------------------------------------------------------------
# Page entry point
# ------------------------------------------------------------

def render(selected_season: str, seasons):
    st.title("🧺 Shot Charts")

    year_start = int(selected_season.split("-")[0])
    if year_start < 2010:
        st.warning("Shot charts are only available for seasons 2010-11 and later.")
        return

    df_stats = load_season_stats_csv(selected_season)

    st.subheader(f"Season: {selected_season}")

    st.markdown("### Player Selection")
    player_id, player_name, team_abbr = build_player_selector(df_stats)
    if player_id is None:
        return

    st.markdown(f"**Selected Player:** {player_name} ({team_abbr}) • ID: {player_id}")
    st.session_state["team_abbr"] = team_abbr

    season_type = st.radio("Season Type", ["Regular Season", "Playoffs"])
    chart_type = st.selectbox("Chart Type", ["Scatter", "Heatmap", "Hexbin"])

    if st.button("Fetch Shot Data"):
        with st.spinner("Fetching shot data..."):
            df_raw = get_player_shots(player_id, selected_season, season_type)

            if df_raw.empty and season_type == "Playoffs":
                st.error(f"{player_name} did not play in the {selected_season} playoffs.")
                return
            elif df_raw.empty:
                st.error("No shot data available for this player and season.")
                return

            df_proc = prepare_for_plotting(df_raw)
            df_games = load_team_game_stats_csv(selected_season)
            df_proc = enrich_hover_with_game_info(df_proc, df_games)

            st.session_state["shots"] = df_proc

    if "shots" not in st.session_state:
        return

    df_proc = st.session_state["shots"]
    df_filtered = apply_simple_filters(df_proc)

    st.markdown("### Shot Chart")
    if df_filtered.empty:
        st.warning("No shots after applying filters.")
    else:
        team_abbr = st.session_state.get("team_abbr")
        if chart_type == "Scatter":
            fig = plot_shots(df_filtered, team_abbr=team_abbr)
        elif chart_type == "Heatmap":
            fig = plot_heatmap(df_filtered, team_abbr=team_abbr)
        else:
            fig = plot_hexbin(df_filtered, team_abbr=team_abbr)

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Season Shooting Summary")
    total, made, missed, fg_pct, by_type, by_zone = compute_season_stats(df_proc)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Attempts", total)
    col2.metric("Made", made)
    col3.metric("Missed", missed)
    col4.metric("FG%", f"{fg_pct:.1f}%")

    st.markdown("#### By Shot Type")
    st.dataframe(by_type.style.format({"fg_pct": "{:.1f}%"}))

    st.markdown("#### By Shot Zone (Basic)")
    st.dataframe(by_zone.style.format({"fg_pct": "{:.1f}%"}))
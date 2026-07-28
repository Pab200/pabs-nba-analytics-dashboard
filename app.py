import streamlit as st
from dashboard.components.styling import load_css
from src.db import run_query

# ------------------------------------------------------------
# Global styling
# ------------------------------------------------------------
load_css()

# ------------------------------------------------------------
# Sidebar: Season selector + Navigation
# ------------------------------------------------------------
st.sidebar.title("NBA Analytics Dashboard")

# Load seasons from database
seasons = run_query("SELECT DISTINCT SEASON FROM season_stats ORDER BY SEASON")

selected_season = st.sidebar.selectbox(
    "Select Season",
    seasons["SEASON"],
    index=len(seasons["SEASON"]) - 1  # default to most recent
)

st.sidebar.markdown("---")

page = st.sidebar.radio("Go to", [
    "League Leaders",
    "Player Analysis",
    "Team Analysis",
    "Compare Players",
    "Team Comparison",
    "Shot Charts",
    "About"
])

# ------------------------------------------------------------
# Page Routing
# ------------------------------------------------------------
if page == "League Leaders":
    import dashboard.pages.league_leaders as page_mod
    page_mod.render(selected_season, seasons)

elif page == "Player Analysis":
    import dashboard.pages.player_analysis as page_mod
    page_mod.render(selected_season, seasons)

elif page == "Team Analysis":
    import dashboard.pages.team_analysis as page_mod
    page_mod.render(selected_season, seasons)

elif page == "Compare Players":
    import dashboard.pages.compare_players as page_mod
    page_mod.render(selected_season, seasons)

elif page == "Team Comparison":
    import dashboard.pages.team_comparison as page_mod
    page_mod.render(selected_season, seasons)

elif page == "Shot Charts":
    import dashboard.pages.shot_charts as page_mod
    page_mod.render(selected_season, seasons)

elif page == "About":
    import dashboard.pages.about as page_mod
    page_mod.render(selected_season, seasons)
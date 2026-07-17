import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# GLOBAL STYLING (CSS)
# -----------------------------
st.markdown("""
<style>

    /* Sidebar background */
    [data-testid="stSidebar"] {
        background-color: #1E1E1E;
    }

    /* Sidebar title ("Navigation") */
    [data-testid="stSidebarContent"] h2 {
        color: white !important;
    }

    /* Make radio label ("Go to") white */
    [data-testid="stSidebar"] .stRadio > label {
        color: white !important;
    }

    /* Make radio options white */
    [data-testid="stSidebar"] .stRadio div {
        color: white !important;
    }

    /* Make season label white */
    [data-testid="stSidebar"] label {
        color: white !important;
    }

    /* Restore selectbox VALUE (the actual selected text) */
    div[data-testid="stSelectbox"] > div > div > div {
        color: black !important;
    }

    /* Page title */
    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: bold;
        margin-bottom: 20px;
    }

</style>
""", unsafe_allow_html=True)

# -----------------------------
# DATABASE + QUERY HELPER
# -----------------------------
conn = sqlite3.connect("nba.db")

def run_query(sql):
    return pd.read_sql_query(sql, conn)

def add_advanced_metrics(df):
    if {"PTS", "FGA", "FTA"}.issubset(df.columns):
        df["TS_PCT"] = df["PTS"] / (2 * (df["FGA"] + 0.44 * df["FTA"]))

    if {"FGM", "FG3M", "FGA"}.issubset(df.columns):
        df["EFG_PCT"] = (df["FGM"] + 0.5 * df["FG3M"]) / df["FGA"]

    if {"AST", "TOV"}.issubset(df.columns):
        df["AST_TOV"] = df["AST"] / df["TOV"].replace(0, pd.NA)

    return df

def color_team_table(df, primary, secondary):
    return df.style.set_properties(
        **{
            "background-color": secondary + "30",
            "color": primary,
            "border-color": primary
        }
    ).set_table_styles([
        {
            "selector": "th",
            "props": [
                ("background-color", primary),
                ("color", "white")
            ]
        }
    ])

# Simple team color mapping
TEAM_COLORS = {
    "ATL": "#E13A3E",
    "BOS": "#007A33",
    "CLE": "#860038",
    "NOP": "#0C2340",
    "CHI": "#CE1141",
    "DAL": "#00538C",
    "DEN": "#0E2240",
    "GSW": "#1D428A",
    "HOU": "#CE1141",
    "LAC": "#1D428A",
    "LAL": "#552583",
    "MIA": "#98002E",
    "MIL": "#00471B",
    "MIN": "#0C2340",
    "BKN": "#000000",
    "NYK": "#006BB6",
    "ORL": "#0077C0",
    "IND": "#002D62",
    "PHI": "#006BB6",
    "PHX": "#1D1160",
    "POR": "#C8102E",
    "SAC": "#5B2C81",
    "SAS": "#000000",
    "OKC": "#007AC1",
    "TOR": "#CE1141",
    "UTA": "#F9A01B",
    "MEM": "#5D76A9",
    "WAS": "#002B5C",
    "DET": "#C8102E",
    "CHA": "#008CA8",
    "NJN": "#C8102E",
    "SEA": "#00653A",
    "NOH": "#008CA8",
    "VAN": "#00B2A9",
    "CHH": "#008CA8",
    "NOK": "#008CA8",
}

SEC_TEAM_COLORS = {
    "ATL": "#000000",
    "BOS": "#BA9653",
    "CLE": "#041E42",
    "NOP": "#85714D",
    "CHI": "#000000",
    "DAL": "#002B5E",
    "DEN": "#FEC524",
    "GSW": "#FFC72C",
    "HOU": "#000000",
    "LAC": "#C8102E",
    "LAL": "#FDB927",
    "MIA": "#000000",
    "MIL": "#EEE1C6",
    "MIN": "#78BE20",
    "BKN": "#FFFFFF",
    "NYK": "#F58426",
    "ORL": "#000000",
    "IND": "#FDBB30",
    "PHI": "#ED174C",
    "PHX": "#E56020",
    "POR": "#000000",
    "SAC": "#707272",
    "SAS": "#C4CED4",
    "OKC": "#F05133",
    "TOR": "#000000",
    "UTA": "#000000",
    "MEM": "#121F32",
    "WAS": "#E31837",
    "DET": "#1D42BA",
    "CHA": "#1D1160",
    "NJN": "#003DA5",
    "SEA": "#FFC200",
    "NOH": "#1D1160",
    "VAN": "#E43C40",
    "CHH": "#1D1160",
    "NOK": "#1D1160",
}

# -----------------------------
# SIDEBAR NAVIGATION
# -----------------------------
st.sidebar.markdown(
    "<h2 style='color: white; margin-bottom: 0.5rem;'>Navigation</h2>",
    unsafe_allow_html=True
)
page = st.sidebar.radio(
    "Go to",
    ["League Leaders", "Player Analysis", "Team Analysis", "About"]
)

# -----------------------------
# SEASON SELECTOR
# -----------------------------
seasons = run_query("""
    SELECT DISTINCT SEASON
    FROM season_stats
    ORDER BY SEASON DESC
""")
selected_season = st.sidebar.selectbox("Season", seasons["SEASON"])

# -----------------------------
# PAGE TITLE
# -----------------------------
st.markdown("<div class='main-title'> NBA Analytics Dashboard</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# ⭐ LEAGUE LEADERS PAGE
# ============================================================
if page == "League Leaders":
    st.header("🏀 League Leaders")
    st.markdown("<br>", unsafe_allow_html=True)

    # ---------- Points ----------
    pts_metric = st.radio(
        "Points metric",
        ["Total Points", "Points Per Game"],
        horizontal=True
    )

    if pts_metric == "Total Points":
        df_points = run_query(f"""
            SELECT PLAYER_NAME, PTS * GP AS TOTAL_POINTS, TEAM_ABBREVIATION
            FROM season_stats
            WHERE SEASON = '{selected_season}'
            ORDER BY TOTAL_POINTS DESC
            LIMIT 10;
        """)
        y_col = "TOTAL_POINTS"
        title = "🔥 Top Scorers (Total Points)"
    else:
        df_points = run_query(f"""
            SELECT PLAYER_NAME, PTS AS PPG, PTS * GP AS TOTAL_POINTS, TEAM_ABBREVIATION
            FROM season_stats
            WHERE SEASON = '{selected_season}'
            ORDER BY TOTAL_POINTS DESC
            LIMIT 10;
        """)
        y_col = "PPG"
        title = "🔥 Top Scorers (Points Per Game)"
    
    colors = [
        TEAM_COLORS.get(team, "#888888")
        for team in df_points["TEAM_ABBREVIATION"]
    ]

    st.subheader(title)
    fig, ax = plt.subplots(figsize=(10,6))
    ax.bar(df_points["PLAYER_NAME"], df_points[y_col], color=colors, edgecolor=[SEC_TEAM_COLORS.get(t, "#000000") for t in df_points["TEAM_ABBREVIATION"]], linewidth=2.5)
    ax.set_xticklabels(df_points["PLAYER_NAME"], rotation=45)
    st.pyplot(fig)
    st.markdown("<br><br>", unsafe_allow_html=True)

    # ---------- Rebounds ----------
    reb_metric = st.radio(
        "Rebounds metric",
        ["Total Rebounds", "Rebounds Per Game", "Offensive REB Per Game", "Defensive REB Per Game"],
        horizontal=True
    )

    df_reb = run_query(f"""
        SELECT PLAYER_NAME,
            REB * GP AS TOTAL_REBOUNDS,
            REB AS REB_PG,
            OREB AS OREB_PG,
            DREB AS DREB_PG, TEAM_ABBREVIATION
        FROM season_stats
        WHERE SEASON = '{selected_season}'
        ORDER BY TOTAL_REBOUNDS DESC
        LIMIT 10;
    """)


    metric_map = {
        "Total Rebounds": ("TOTAL_REBOUNDS", "💪 Top Rebounders (Total)"),
        "Rebounds Per Game": ("REB_PG", "💪 Top Rebounders (Per Game)"),
        "Offensive REB Per Game": ("OREB_PG", "💪 Top Offensive Rebounders"),
        "Defensive REB Per Game": ("DREB_PG", "💪 Top Defensive Rebounders"),
    }

    colors = [
        TEAM_COLORS.get(team, "#888888")
        for team in df_reb["TEAM_ABBREVIATION"]
    ]

    y_col, title = metric_map[reb_metric]
    st.subheader(title)
    fig, ax = plt.subplots(figsize=(10,6))
    ax.bar(df_reb["PLAYER_NAME"], df_reb[y_col], color=colors, edgecolor=[SEC_TEAM_COLORS.get(t, "#000000") for t in df_points["TEAM_ABBREVIATION"]], linewidth=2.5)
    ax.set_xticklabels(df_reb["PLAYER_NAME"], rotation=45)
    st.pyplot(fig)
    st.markdown("<br><br>", unsafe_allow_html=True)

    # ---------- Assists ----------
    ast_metric = st.radio(
        "Assists metric",
        ["Total Assists", "Assists Per Game"],
        horizontal=True
    )

    df_ast = run_query(f"""
        SELECT PLAYER_NAME,
            AST * GP AS TOTAL_ASSISTS,
            AST AS AST_PG, TEAM_ABBREVIATION
        FROM season_stats
        WHERE SEASON = '{selected_season}'
        ORDER BY TOTAL_ASSISTS DESC
        LIMIT 10;
    """)

    if ast_metric == "Total Assists":
        y_col, title = "TOTAL_ASSISTS", "🎯 Top Assist Leaders (Total)"
    else:
        y_col, title = "AST_PG", "🎯 Top Assist Leaders (Per Game)"
    
    colors = [
        TEAM_COLORS.get(team, "#888888")
        for team in df_ast["TEAM_ABBREVIATION"]
    ]

    st.subheader(title)
    fig, ax = plt.subplots(figsize=(10,6))
    ax.bar(df_ast["PLAYER_NAME"], df_ast[y_col], color=colors, edgecolor=[SEC_TEAM_COLORS.get(t, "#000000") for t in df_points["TEAM_ABBREVIATION"]], linewidth=2.5)
    ax.set_xticklabels(df_ast["PLAYER_NAME"], rotation=45)
    st.pyplot(fig)
    st.markdown("<br><br>", unsafe_allow_html=True)

    # ---------- FG / 3P / FGA / FGM ----------
    fg_metric = st.radio(
        "Shooting metric",
        ["FG%", "3P%", "FGA", "FGM"],
        horizontal=True
    )

    df_fg = run_query(f"""
        SELECT PLAYER_NAME, FG_PCT, FG3_PCT, FGA, FGM, TEAM_ABBREVIATION
            FROM season_stats
            WHERE SEASON = '{selected_season}' AND MIN >= 15
            ORDER BY FG_PCT DESC
            LIMIT 10;
    """)

    metric_map = {
        "FG%": ("FG_PCT", "🎯 Field Goal Percentage (min 15 MPG)"),
        "3P%": ("FG3_PCT", "🎯 Three-Point Percentage (min 15 MPG)"),
        "FGA": ("FGA", "🎯 Field Goal Attempts (min 15 MPG)"),
        "FGM": ("FGM", "🎯 Field Goals Made (min 15 MPG)"),
    }

    colors = [
        TEAM_COLORS.get(team, "#888888")
        for team in df_fg["TEAM_ABBREVIATION"]
    ]

    y_col, title = metric_map[fg_metric]
    st.subheader(title)
    fig, ax = plt.subplots(figsize=(10,6))
    ax.bar(df_fg["PLAYER_NAME"], df_fg[y_col], color=colors, edgecolor=[SEC_TEAM_COLORS.get(t, "#000000") for t in df_points["TEAM_ABBREVIATION"]], linewidth=2.5)
    ax.set_xticklabels(df_fg["PLAYER_NAME"], rotation=45)
    st.pyplot(fig)
    st.markdown("<br><br>", unsafe_allow_html=True)

    # ---------- Fantasy, Steals, Blocks, TOV, Minutes ----------
    st.subheader("📊 Other League Leaders")

    # Fantasy
    fantasy_metric = st.radio(
        "Fantasy metric",
        ["Total Fantasy Points", "Fantasy Points Per Game"],
        horizontal=True
    )

    df_fantasy = run_query(f"""
        SELECT PLAYER_NAME,
            NBA_FANTASY_PTS * GP AS TOTAL_FANTASY,
            NBA_FANTASY_PTS AS FANTASY_PG, TEAM_ABBREVIATION
        FROM season_stats
        WHERE SEASON = '{selected_season}'
        ORDER BY TOTAL_FANTASY DESC
        LIMIT 10;
    """)

    colors = [
        TEAM_COLORS.get(team, "#888888")
        for team in df_fantasy["TEAM_ABBREVIATION"]
    ]

    y_col = "TOTAL_FANTASY" if fantasy_metric == "Total Fantasy Points" else "FANTASY_PG"
    fig, ax = plt.subplots(figsize=(19,6))
    ax.bar(df_fantasy["PLAYER_NAME"], df_fantasy[y_col], color=colors, edgecolor=[SEC_TEAM_COLORS.get(t, "#000000") for t in df_points["TEAM_ABBREVIATION"]], linewidth=2.5)
    ax.set_xticklabels(df_fantasy["PLAYER_NAME"], rotation=45)
    st.pyplot(fig)

    # Steals
    steals_metric = st.radio(
        "Steals metric",
        ["Total Steals", "Steals Per Game"],
        horizontal=True
    )

    df_stl = run_query(f"""
        SELECT PLAYER_NAME,
            STL * GP AS TOTAL_STEALS,
            STL AS STL_PG, TEAM_ABBREVIATION
        FROM season_stats
        WHERE SEASON = '{selected_season}'
        ORDER BY TOTAL_STEALS DESC
        LIMIT 10;
    """)

    colors = [
        TEAM_COLORS.get(team, "#888888")
        for team in df_stl["TEAM_ABBREVIATION"]
    ]

    y_col = "TOTAL_STEALS" if steals_metric == "Total Steals" else "STL_PG"
    fig, ax = plt.subplots(figsize=(10,6))
    ax.bar(df_stl["PLAYER_NAME"], df_stl[y_col], color=colors, edgecolor=[SEC_TEAM_COLORS.get(t, "#000000") for t in df_points["TEAM_ABBREVIATION"]], linewidth=2.5)
    ax.set_xticklabels(df_stl["PLAYER_NAME"], rotation=45)
    st.pyplot(fig)

    # Blocks
    blocks_metric = st.radio(
        "Blocks metric",
        ["Total Blocks", "Blocks Per Game"],
        horizontal=True
    )

    df_blk = run_query(f"""
        SELECT PLAYER_NAME,
            BLK * GP AS TOTAL_BLOCKS,
            BLK AS BLK_PG, TEAM_ABBREVIATION
        FROM season_stats
        WHERE SEASON = '{selected_season}'
        ORDER BY TOTAL_BLOCKS DESC
        LIMIT 10;
    """)

    colors = [
        TEAM_COLORS.get(team, "#888888")
        for team in df_blk["TEAM_ABBREVIATION"]
    ]

    y_col = "TOTAL_BLOCKS" if blocks_metric == "Total Blocks" else "BLK_PG"
    fig, ax = plt.subplots(figsize=(10,6))
    ax.bar(df_blk["PLAYER_NAME"], df_blk[y_col], color=colors, edgecolor=[SEC_TEAM_COLORS.get(t, "#000000") for t in df_points["TEAM_ABBREVIATION"]], linewidth=2.5)
    ax.set_xticklabels(df_blk["PLAYER_NAME"], rotation=45)
    st.pyplot(fig)

    # Turnovers
    tov_metric = st.radio(
        "Turnovers metric",
        ["Total Turnovers", "Turnovers Per Game"],
        horizontal=True
    )

    df_tov = run_query(f"""
        SELECT PLAYER_NAME,
            TOV * GP AS TOTAL_TOV,
            TOV AS TOV_PG, TEAM_ABBREVIATION
        FROM season_stats
        WHERE SEASON = '{selected_season}'
        ORDER BY TOTAL_TOV DESC
        LIMIT 10;
    """)

    colors = [
        TEAM_COLORS.get(team, "#888888")
        for team in df_tov["TEAM_ABBREVIATION"]
    ]

    y_col = "TOTAL_TOV" if tov_metric == "Total Turnovers" else "TOV_PG"
    fig, ax = plt.subplots(figsize=(10,6))
    ax.bar(df_tov["PLAYER_NAME"], df_tov[y_col], color=colors, edgecolor=[SEC_TEAM_COLORS.get(t, "#000000") for t in df_points["TEAM_ABBREVIATION"]], linewidth=2.5)
    ax.set_xticklabels(df_tov["PLAYER_NAME"], rotation=45)
    st.pyplot(fig)

    # Minutes
    min_metric = st.radio(
        "Minutes metric",
        ["Total Minutes", "Minutes Per Game"],
        horizontal=True
    )

    df_min = run_query(f"""
        SELECT PLAYER_NAME,
            MIN * GP AS TOTAL_MIN,
            MIN AS MIN_PG, TEAM_ABBREVIATION
        FROM season_stats
        WHERE SEASON = '{selected_season}'
        ORDER BY TOTAL_MIN DESC
        LIMIT 10;
    """)

    colors = [
        TEAM_COLORS.get(team, "#888888")
        for team in df_min["TEAM_ABBREVIATION"]
    ]

    y_col = "TOTAL_MIN" if min_metric == "Total Minutes" else "MIN_PG"
    fig, ax = plt.subplots(figsize=(10,6))
    ax.bar(df_min["PLAYER_NAME"], df_min[y_col], color=colors, edgecolor=[SEC_TEAM_COLORS.get(t, "#000000") for t in df_points["TEAM_ABBREVIATION"]], linewidth=2.5)
    ax.set_xticklabels(df_min["PLAYER_NAME"], rotation=45)
    st.pyplot(fig)

    # Advanced metrics
    adv_metric = st.radio(
        "Advanced metric",
        ["TS%", "eFG%", "AST/TOV"],
        horizontal=True
    )

    df_adv = run_query(f"""
        SELECT PLAYER_NAME, TEAM_ABBREVIATION, 
            PTS, FGA, FTA, FGM, FG3M, AST, TOV
        FROM season_stats
        WHERE SEASON = '{selected_season}' AND MIN >= 15
    """)
    df_adv = add_advanced_metrics(df_adv)

    metric_map = {
        "TS%": ("TS_PCT", "🔥 True Shooting % Leaders"),
        "eFG%": ("EFG_PCT", "🔥 Effective FG % Leaders"),
        "AST/TOV": ("AST_TOV", "🔥 Assist-to-Turnover Ratio Leaders"),
    }

    y_col, title = metric_map[adv_metric]
    df_plot = df_adv.sort_values(y_col, ascending=False).head(10)
    colors = [TEAM_COLORS.get(t, "#888888") for t in df_plot["TEAM_ABBREVIATION"]]
    st.subheader(title)
    fig, ax = plt.subplots(figsize=(10,6))
    ax.bar(df_plot["PLAYER_NAME"], df_plot[y_col], color=colors,
           edgecolor=[SEC_TEAM_COLORS.get(t, "#000000") for t in df_plot["TEAM_ABBREVIATION"]],
           linewidth=2.5)
    ax.set_xticklabels(df_plot["PLAYER_NAME"], rotation=45)
    st.pyplot(fig)

# ============================================================
# ⭐ PLAYER ANALYSIS PAGE
# ============================================================
elif page == "Player Analysis":
    st.header("🔍 Player Analysis")
    st.markdown("<br>", unsafe_allow_html=True)

    players = run_query("SELECT DISTINCT PLAYER_NAME FROM season_stats ORDER BY PLAYER_NAME")
    player = st.selectbox("Select a Player", players["PLAYER_NAME"])

    if player:
        df_player = run_query(f"""
            SELECT PLAYER_NAME, TEAM_ABBREVIATION, AGE, GP, MIN,
                PTS, REB, AST, STL, BLK, TOV, FG_PCT, FG3_PCT,
                NBA_FANTASY_PTS,
                FGA, FGM, FG3M, FTA
            FROM season_stats
            WHERE PLAYER_NAME = '{player}'
            AND SEASON = '{selected_season}'
        """)
        if df_player.empty:
            st.error(f"{player} has no stats in {selected_season}. Try a different season or player.")
        else:
            df_player = add_advanced_metrics(df_player)
            team = df_player["TEAM_ABBREVIATION"].iloc[0]
            primary = TEAM_COLORS.get(team, "#888888")
            secondary = SEC_TEAM_COLORS.get(team, "#AAAAAA")

            st.subheader("Player Summary")
            styled_player = color_team_table(df_player, primary, secondary)
            st.dataframe(styled_player)

            view = st.radio(
                "View type",
                ["Basic Stats", "Advanced Metrics"],
                horizontal=True
            )

            if not df_player.empty:
                if view == "Basic Stats":
                    stats = ["PTS", "REB", "AST", "STL", "BLK"]
                    values = [df_player[s].iloc[0] for s in stats]
                    st.subheader("Key Stats (Per Game)")
                    fig, ax = plt.subplots(figsize=(10,6))
                    ax.bar(stats, values, color=primary, edgecolor=secondary, linewidth=3)
                    st.pyplot(fig)
                else:
                    adv_stats = ["TS_PCT", "EFG_PCT", "AST_TOV"]
                    available = [s for s in adv_stats if s in df_player.columns]
                    values = [df_player[s].iloc[0] for s in available]

                    st.subheader("Advanced Metrics")
                    fig, ax = plt.subplots(figsize=(10,6))
                    ax.bar(available, values, color=primary, edgecolor=secondary, linewidth=3)
                    st.pyplot(fig)

                    st.markdown("""
                    **TS%**: True Shooting % - scoring efficiency including threes and free throws.
                    **eFG%**: Effective FG % - adjusts FG% for the extra value of 3s.
                    **AST/TOV**: How often assists come relative to turnovers.
                    """)

# ============================================================
# ⭐ TEAM ANALYSIS PAGE
# ============================================================
elif page == "Team Analysis":
    st.header("🏙️ Team Analysis")
    st.markdown("<br>", unsafe_allow_html=True)

    teams = run_query("SELECT DISTINCT TEAM_ABBREVIATION FROM season_stats")
    team = st.selectbox("Choose a team", teams["TEAM_ABBREVIATION"])

    team_info = run_query(f"""
        SELECT full_name, city, state, nickname, year_founded, year_closed
        FROM teams
        WHERE abbreviation = '{team}'
    """).iloc[0]

    primary = TEAM_COLORS.get(team, "#333333")
    secondary = SEC_TEAM_COLORS.get(team, "#555555")

    st.subheader("Team Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**City:** {team_info['city']}")
        st.write(f"**State:** {team_info['state']}")

    with col2:
        st.write(f"**Nickname:** {team_info['nickname']}")
        st.write(f"**Year Founded:** {team_info['year_founded']}")
        st.write(f"**Year Closed:** {team_info['year_closed'] if team_info['year_closed'] else 'Active'}")

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.subheader("Team Season Statistics")

    df_team = run_query(f"""
        SELECT PLAYER_NAME, PTS, REB, AST, FG_PCT
        FROM season_stats
        WHERE TEAM_ABBREVIATION = '{team}'
        AND SEASON = '{selected_season}'
    """)
    styled_df = color_team_table(df_team, primary, secondary)
    st.dataframe(styled_df)

    fig, ax = plt.subplots(figsize=(10,6))
    ax.bar(df_team["PLAYER_NAME"], df_team["PTS"], edgecolor=secondary, linewidth=3)
    ax.set_xticklabels(df_team["PLAYER_NAME"], rotation=45)
    st.pyplot(fig)

# ============================================================
# ⭐ ABOUT PAGE
# ============================================================
elif page == "About":
    st.header("ℹ️ About This Project")

    st.write("""
    This NBA Analytics Dashboard was built to explore multiple seasons using real SQL queries, Python, and Streamlit.
             
    **Technologies Used**
    - SQLite
    - Pandas
    - Matplotlib
    - Streamlit
             
    **Future Ideas**
    - Player Images
    - Player Projections
    - Fantasy Basketball
    - Interactive Shot Charts
    - Player Comparison
    - Team Comparison & Filters
    """)
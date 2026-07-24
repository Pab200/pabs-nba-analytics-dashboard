# 🏀 NBA Analytics Dashboard
A fully modular, multi‑page NBA analytics platform built with Python, SQLite, and Streamlit.  
This project provides deep statistical insights into players, teams, seasons, and league trends using a clean, professional architecture.

---

## 📌 Overview
This dashboard allows you to explore NBA data across multiple seasons with:

- League leaders (PTS, REB, AST, shooting, fantasy, advanced metrics)
- Player analysis (basic + advanced metrics)
- Team analysis (ORtg, DRtg, Pace, possessions, roster stats)
- Player comparison (multi‑player, multi‑season)
- Team comparison (multi‑team, multi‑season)
- Cross‑season support
- Automatic team color styling
- Reproducible SQLite database pipeline

The project supports **modern NBA Stats API seasons** and **older Basketball Reference seasons**, normalized into a unified schema.

---

## 🏗️ Architecture

### Project Structure
pabs-nba-analytics-dashboard/
│
├── app.py                         # Streamlit entry point (root-level)
│
├── dashboard/
│   ├── init.py
│   ├── components/
│   │   ├── init.py
│   │   └── styling.py             # Global CSS + table styling
│   │
│   └── pages/                     # Modular Streamlit pages
│       ├── init.py
│       ├── league_leaders.py
│       ├── player_analysis.py
│       ├── team_analysis.py
│       ├── compare_players.py
│       ├── team_comparison.py
│       └── about.py
│
├── src/
│   ├── init.py
│   ├── db.py                      # SQLite connection + query helper
│   ├── metrics.py                 # TS%, eFG%, AST/TOV, etc.
│   ├── colors.py                  # Team color system
│   ├── utils.py                   # Season helpers + misc utilities
│   └── team_stats.py              # ORtg, DRtg, Pace, possession logic
│
├── src/data_pipeline/
│   ├── init.py
│   ├── create_database.py         # Build nba.db from raw CSVs
│   ├── data_loader.py             # Load new seasons into database
│   └── normalize_br.py            # Normalize Basketball Reference CSVs
│
├── data/
│   ├── raw/                       # Raw CSVs (nba_api + BR)
│   └── processed/                 # Cleaned tables (optional)
│
├── notebooks/                     # Jupyter notebooks for exploration
├── reports/                       # Generated charts + summaries
├── images/                        # Dashboard screenshots
│
├── requirements.txt               # Project dependencies
└── README.md

---

## ✨ Features

### Dashboard Pages
- **League Leaders**  
  - Points (Total / Per Game)  
  - Rebounds (Total / Per Game / OREB / DREB)  
  - Assists (Total / Per Game)  
  - Shooting (FG%, 3P%, FGA, FGM)  
  - Fantasy Points  
  - Steals, Blocks, Turnovers, Minutes  
  - Advanced Metrics (TS%, eFG%, AST/TOV)

- **Player Analysis**  
  - Basic stats  
  - Advanced metrics  
  - Team color‑styled tables  
  - Per‑game and efficiency charts

- **Team Analysis**  
  - ORtg, DRtg, Pace, Possessions  
  - Team roster stats  
  - Team color‑styled tables  
  - Team scoring charts

- **Compare Players**  
  - Unlimited players  
  - Cross‑season comparison  
  - Per‑game stats  
  - Shooting & efficiency charts  
  - Advanced metrics

- **Team Comparison**  
  - Unlimited teams  
  - Cross‑season comparison  
  - Team summaries  
  - Comparison table  
  - Grouped bar charts (ORtg, DRtg, Pace, REB, AST, 3PA)

- **About Page**

---

## 📁 Data Sources

### NBA Stats API (via `nba_api`)
Used for:
- Modern seasons (1996–present)
- Full per‑game stats
- Team game logs (2010–present)

### Basketball Reference (manual CSVs)
Used for:
- Older seasons (pre‑1996)
- Normalized using `normalize_br.py`

### Raw Data Files
- `players.csv`
- `teams.csv`
- `rookies.csv`
- `season_stats_*.csv`
- `team_game_stats_*.csv`
- `br_*.csv` (Basketball Reference)

---

## 🚀 Running the Dashboard

### 1. Clone the repository
git clone https://github.com/pabs-nba-analytics-dashboard.git (github.com in Bing)
cd pabs-nba-analytics-dashboard

### 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate      # Windows

### 3. Install dependencies
pip install -r requirements.txt

### 4. Run the dashboard
streamlit run app.py

---

## 🛠️ Data Pipeline

### Build the database from scratch
python src/data_pipeline/create_database.py

### Load new seasons
Place new CSVs into `data/raw/`:

- `season_stats_YYYY-YY.csv`
- `team_game_stats_YYYY-YY.csv`

Then run:

python src/data_pipeline/data_loader.py

### Normalize Basketball Reference CSVs
python src/data_pipeline/normalize_br.py

This converts BR data into the NBA Stats API schema.

---

## 🛣️ Roadmap
- Add player images  
- Add team logos  
- Add shot charts  
- Add predictive analytics  
- Add opponent filters  
- Add month-by-month splits  
- Add playoff mode  

---

## 👤 Author
**Pablo**  
Chicago IL, USA  
NBA Analytics Enthusiast & Data Engineer

GitHub: https://github.com/pabs-nba-analytics-dashboard

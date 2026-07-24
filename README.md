# **pabs-nba-analytics-dashboard**
*A modern NBA analytics platform built with Python, SQL, and Streamlit.*

## 📌 Overview
This project is a full end-to-end NBA analytics system designed to explore player performance, team trends, and season-level insights using:

- Python for data ingestion and cleaning  
- SQLite for structured storage and SQL analysis  
- Pandas for transformation  
- Matplotlib / Seaborn for visualizations  
- Streamlit for an interactive dashboard  

The goal is to build a reproducible, scalable analytics pipeline that can support multiple NBA seasons and advanced statistical comparisons.

---

## 🏗️ Architecture

### Data Pipeline
1. **Data Acquisition**  
   - Pull raw NBA data using `nba_api`  
   - Save CSVs into `data/raw/`

2. **Database Construction**  
   - Build `nba.db` using Python + SQLite  
   - Normalize tables (players, teams, season_stats, rookies)

3. **Analysis Notebooks**  
   - SQL exploration  
   - Pandas transformations  
   - Visualizations and advanced metrics

4. **Interactive Dashboard**  
   - Player comparison  
   - Team insights  
   - Season-level summaries  
   - Multi-season support

---

## ✨ Features
- Multi-season support  
- Player comparison tool  
- Team insights and roster analysis  
- Advanced statistics (PER, TS%, usage rate, etc.)  
- SQL + Pandas hybrid analysis  
- Reproducible data pipeline  
- Visualizations for scoring, efficiency, shooting, and more  

---

## 📁 Project Structure
pabs-nba-analytics-dashboard/
│
├── dashboard/           # Streamlit app + pages
├── data/
│   ├── raw/             # Raw CSVs from nba_api
│   ├── processed/       # Cleaned tables + database
│
├── notebooks/           # Jupyter notebooks for analysis
│   ├── 01_data_ingestion.ipynb
│   ├── 02_sql_analysis.ipynb
│   ├── 03_visualizations.ipynb
│   └── 04_advanced_stats.ipynb
│
├── src/                 # Python modules for logic
│   ├── data_loader.py
│   ├── metrics.py
│   ├── utils.py
│   └── comparison.py
│
├── reports/             # Generated charts + summaries
├── images/              # Dashboard screenshots
│
├── app.py               # Streamlit entry point
├── nba.db               # SQLite database
├── requirements.txt     # Project dependencies
└── README.md

---

## 📊 Data Sources
This project uses data from:

- `nba_api` (official NBA stats API wrapper)  
- Custom CSVs generated from API calls  
- SQLite database built from raw data  

Raw data includes:

- `players.csv` — full NBA player list  
- `teams.csv` — NBA team metadata  
- `season_stats_2025-26.csv` — full season stats  
- `rookies.csv` — 2025 draft class  

---

## 🚀 Running the Project Locally

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

## 🛣️ Roadmap
- Add all NBA seasons (full historical dataset)  
- Add game logs for deeper analysis  
- Add team comparison page  
- Add player similarity model (cosine similarity)  
- Add predictive analytics (simple models)  
- Add API mode for external apps  
- Add dark mode UI  

---

## 👤 Author
**Pablo**  
Chicago IL, USA  
NBA Analytics Enthusiast & Data Engineer  
GitHub: https://github.com/pabs-nba-analytics-dashboard

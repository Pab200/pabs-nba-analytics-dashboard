import pandas as pd
import hashlib

def normalize_br_csv(input_path: str, output_path: str, season: str):
    """
    Normalize a Basketball Reference per-game CSV into the NBA Stats API schema.
    """

    # Load BR CSV
    df = pd.read_csv(input_path)

    # Remove ranking column if present
    df = df.drop(columns=["Rk"], errors="ignore")

    three_point_cols = {
        "3P": 0.0,
        "3PA": 0.0,
        "3P%": None,
        "OREB": 0.0,
        "DREB": 0.0,
        "TOV": 0.0,
        "STL": 0.0,
        "BLK": 0.0,
    }
    for col, default in three_point_cols.items():
        if col not in df.columns:
            df[col] = default

    # Create synthetic PLAYER_ID using a stable hash
    def make_player_id(name):
        return int(hashlib.sha256(name.encode()).hexdigest(), 16) % (10**9)
    
    df["PLAYER_ID"] = df["Player"].apply(make_player_id)

    # Rename BR columns -> NBA API columns
    rename_map = {
        "Player": "PLAYER_NAME",
        "Age": "AGE",
        "Team": "TEAM_ABBREVIATION",
        "G": "GP",
        "MP": "MIN",
        "FG": "FGM",
        "FGA": "FGA",
        "FG%": "FG_PCT",
        "3P": "FG3M",
        "3PA": "FG3A",
        "3P%": "FG3_PCT",
        "FT": "FTM",
        "FTA": "FTA",
        "FT%": "FT_PCT",
        "ORB": "OREB",
        "DRB": "DREB",
        "TRB": "REB",
        "AST": "AST",
        "STL": "STL",
        "BLK": "BLK",
        "TOV": "TOV",
        "PF": "PF",
        "PTS": "PTS"
    }
    df = df.rename(columns=rename_map)

    # Add missing modern-era fields as None
    missing_cols = [
        "NICKNAME","TEAM_ID","W","L","W_PCT","BLKA","PFD","PLUS_MINUS",
        "NBA_FANTASY_PTS","DD2","TD3","WNBA_FANTASY_PTS",
        "GP_RANK","W_RANK","L_RANK","W_PCT_RANK", "MIN_RANK","FGM_RANK",
        "FGA_RANK","FG_PCT_RANK","FG3M_RANK","FG3A_RANK","FG3_PCT_RANK",
        "FTM_RANK","FTA_RANK","FT_PCT_RANK","OREB_RANK","DREB_RANK",
        "REB_RANK","AST_RANK","TOV_RANK","STL_RANK","BLK_RANK","BLKA_RANK",
        "PF_RANK","PFD_RANK","PTS_RANK","PLUS_MINUS_RANK",
        "NBA_FANTASY_PTS_RANK","DD2_RANK","TD3_RANK","WNBA_FANTASY_PTS_RANK",
        "TEAM_COUNT"
    ]

    for col in missing_cols:
        df[col] = None
    
    # Add season column
    df["SEASON"] = season

    # Reorder columns to match NBA API exactly
    # Reorder columns to match NBA API exactly
    final_cols = [
        "PLAYER_ID","PLAYER_NAME","NICKNAME","TEAM_ID","TEAM_ABBREVIATION",
        "AGE","GP","W","L","W_PCT","MIN","FGM","FGA","FG_PCT","FG3M","FG3A",
        "FG3_PCT","FTM","FTA","FT_PCT","OREB","DREB","REB","AST","TOV","STL",
        "BLK","BLKA","PF","PFD","PTS","PLUS_MINUS","NBA_FANTASY_PTS","DD2",
        "TD3","WNBA_FANTASY_PTS","GP_RANK","W_RANK","L_RANK","W_PCT_RANK",
        "MIN_RANK","FGM_RANK","FGA_RANK","FG_PCT_RANK","FG3M_RANK","FG3A_RANK",
        "FG3_PCT_RANK","FTM_RANK","FTA_RANK","FT_PCT_RANK","OREB_RANK",
        "DREB_RANK","REB_RANK","AST_RANK","TOV_RANK","STL_RANK","BLK_RANK",
        "BLKA_RANK","PF_RANK","PFD_RANK","PTS_RANK","PLUS_MINUS_RANK",
        "NBA_FANTASY_PTS_RANK","DD2_RANK","TD3_RANK","WNBA_FANTASY_PTS_RANK",
        "TEAM_COUNT","SEASON"
    ]

    df = df[final_cols]

    # Save normalized CSV
    df.to_csv(output_path, index=False)
    print(f"Normalized CSV saved to {output_path}")

normalize_br_csv(
    input_path="data/raw/br_1995_per_game.csv",
    output_path="data/raw/season_stats_1951-52.csv",
    season="1951-52"
)
import os
import pandas as pd

from src.fantasy.consistency import analyze_player_consistency
from src.fantasy.scoring import DEFAULT_SCORING
from src.utils import load_all_seasons, RAW_DIR  # Clean import from utils

def load_game_logs_for_season(season):
    """Load player game logs for a given season."""
    path = f"data/player_game_logs/{season}/player_game_logs{season}.csv"
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)

def add_consistency_features(df_train):
    """
    Adds consistency features for the CURRENT season.
    df_train is the Phase 4 dataset (current → next season).
    """

    # Extract unique seasons from CURRENT season column
    seasons = sorted(df_train["SEASON_current"].unique())

    # Dictionary to store consistency metrics per (PLAYER_ID, SEASON)
    consistency_map = {}

    for season in seasons:
        df_logs = load_game_logs_for_season(season)
        if df_logs is None:
            continue

        # Compute fantasy points using default scoring
        scoring = DEFAULT_SCORING
        df_logs["FANTASY_PTS"] = (
            df_logs["PTS"] * scoring["PTS"] +
            df_logs["REB"] * scoring["REB"] +
            df_logs["AST"] * scoring["AST"] +
            df_logs["STL"] * scoring["STL"] +
            df_logs["BLK"] * scoring["BLK"] +
            df_logs["TOV"] * scoring["TOV"]
        )

        for player_id in df_logs["PLAYER_ID"].unique():
            df_player = df_logs[df_logs["PLAYER_ID"] == player_id]

            if len(df_player) < 5:
                continue

            df_with_fp, metrics = analyze_player_consistency(df_player, scoring)

            consistency_map[(player_id, season)] = {
                "CONSISTENCY_MEAN_current": metrics["mean_fp"],
                "CONSISTENCY_STD_current": metrics["std_fp"], # ensure key matches your dict
                "CONSISTENCY_CV_current": metrics["cv_fp"],
                "CONSISTENCY_LABEL_current": metrics["label"]
            }

    # Convert dictionary → DataFrame (OUTSIDE the season loop)
    if not consistency_map:
        return df_train

    df_consistency = pd.DataFrame([
        {
            "PLAYER_ID": pid,
            "SEASON_current": season,
            **vals
        }
        for (pid, season), vals in consistency_map.items()
    ])

    # Merge into training dataset
    df_train = df_train.merge(
        df_consistency,
        on=["PLAYER_ID", "SEASON_current"],
        how="left"
    )

    return df_train

from src.fantasy.boom_bust  import analyze_boom_bust
from src.fantasy.scoring import DEFAULT_SCORING

def add_boom_bust_features(df_train):
    """
    Adds Boom/Bust features for the CURRENT season.
    df_train is the Phase 4 dataset (current → next season).
    """

    seasons = sorted(df_train["SEASON_current"].unique())

    boom_map = {}

    for season in seasons:
        df_logs = load_game_logs_for_season(season)
        if df_logs is None:
            continue

        # Compute fantasy points using default scoring
        scoring = DEFAULT_SCORING
        df_logs["FANTASY_PTS"] = (
            df_logs["PTS"] * scoring["PTS"] +
            df_logs["REB"] * scoring["REB"] +
            df_logs["AST"] * scoring["AST"] +
            df_logs["STL"] * scoring["STL"] +
            df_logs["BLK"] * scoring["BLK"] +
            df_logs["TOV"] * scoring["TOV"]
        )

        for player_id in df_logs["PLAYER_ID"].unique():
            df_player = df_logs[df_logs["PLAYER_ID"] == player_id]

            if len(df_player) < 5:
                continue

            df_bb, metrics = analyze_boom_bust(df_player)

            boom_map[(player_id, season)] = {
                "BOOM_RATE_current": metrics["boom_rate"],
                "BUST_RATE_current": metrics["bust_rate"],
                "NEUTRAL_RATE_CURRENT": metrics["neutral_rate"],
                "BOOM_THRESHOLD_current": metrics["boom_threshold"],
                "BUST_THRESHOLD_current": metrics["bust_threshold"],
                "MINUTES_RELIABILITY_current": metrics["minutes_reliability"],
                "BOOM_BUST_LABEL_current": metrics["classification"]
            }

    # Convert dictionary → DataFrame
    df_boom = pd.DataFrame([
        {
            "PLAYER_ID": pid,
            "SEASON_current": season,
            **vals
        }
        for (pid, season), vals in boom_map.items()
    ])

    # Merge into training dataset
    df_train = df_train.merge(
        df_boom,
        on=["PLAYER_ID", "SEASON_current"],
        how="left"
    )

    return df_train

def load_shots_for_season(season):
    """Load all regular-season shot data for a given season."""
    base_dir = f"data/shots/{season}/regular"
    if not os.path.exists(base_dir):
        return None

    frames = []
    for file in os.listdir(base_dir):
        if file.endswith(".csv"):
            path = os.path.join(base_dir, file)
            df  = pd.read_csv(path)
            frames.append(df)

        if not frames:
            return None

        return pd.concat(frames, ignore_index=True)

def add_shot_distribution_features(df_train):
    """
    Adds shot distribution features (rim/mid/3P frequency) for the CURRENT season.
    """

    seasons = sorted(df_train["SEASON_current"].unique())
    dist_map = {}

    for season in seasons:
        df_shots = load_shots_for_season(season)
        if df_shots is None:
            continue

        # Use only attempted shots
        df_shots = df_shots[df_shots["SHOT_ATTEMPTED_FLAG"] == 1]

        for player_id in df_shots["PLAYER_ID"].unique():
            df_p = df_shots[df_shots["PLAYER_ID"] == player_id]

            if len(df_p) < 20:
                continue

            total = len(df_p)

            rim = df_p["SHOT_ZONE_BASIC"].isin(["Restricted Area", "In The Paint (Non-RA)"]).sum()
            mid = df_p["SHOT_ZONE_BASIC"].isin(["Mid-Range"]).sum()
            three = df_p["SHOT_ZONE_BASIC"].isin(["Above the Break 3", "Corner 3", "Backcourt"]).sum()

            dist_map[(player_id, season)] = {
                "SHOT_RIM_FREQ_current": rim / total,
                "SHOT_MID_FREQ_current": mid / total,
                "SHOT_3P_FREQ_current": three / total,
            }

    df_dist = pd.DataFrame([
        {
            "PLAYER_ID": pid,
            "SEASON_current": season,
            **vals
        }
        for (pid, season), vals in dist_map.items()
    ])

    df_train = df_train.merge(
        df_dist,
        on=["PLAYER_ID", "SEASON_current"],
        how="left"
    )

    return df_train

def add_shot_efficiency_features(df_train):
    """
    Adds shot efficiency features (rim/mid/3P FG%) for the CURRENT season.
    """

    seasons = sorted(df_train["SEASON_current"].unique())
    eff_map = {}

    for season in seasons:
        df_shots = load_shots_for_season(season)
        if df_shots is None:
            continue

        # Only attempted shots
        df_shots = df_shots[df_shots["SHOT_ATTEMPTED_FLAG"] == 1]

        for player_id in df_shots["PLAYER_ID"].unique():
            df_p = df_shots[df_shots["PLAYER_ID"] == player_id]

            if len(df_p) < 20:
                continue

            # Zone masks
            rim_mask = df_p["SHOT_ZONE_BASIC"].isin(["Restricted Area", "In The Paint (Non-RA)"])
            mid_mask = df_p["SHOT_ZONE_BASIC"].isin(["Mid-Range"])
            three_mask = df_p["SHOT_ZONE_BASIC"].isin(["Above the Break 3", "Corner 3", "Backcourt"])

            # Efficiency = makes / attempts
            def eff(mask):
                attempts = mask.sum()
                if attempts == 0:
                    return None
                makes = df_p.loc[mask, "SHOT_MADE_FLAG"].sum()
                return makes / attempts

            rim_eff = eff(rim_mask)
            mid_eff = eff(mid_mask)
            three_eff = eff(three_mask)

            eff_map[(player_id, season)] = {
                "SHOT_RIM_EFF_current": rim_eff,
                "SHOT_MID_EFF_current": mid_eff,
                "SHOT_3P_EFF_current": three_eff,
            }

    # Convert dictionary → DataFrame
    df_eff = pd.DataFrame([
        {
            "PLAYER_ID": pid,
            "SEASON_current": season,
            **vals
        }
        for (pid, season), vals in eff_map.items()
    ])

    # Merge into training dataset
    df_train = df_train.merge(
        df_eff,
        on=["PLAYER_ID", "SEASON_current"],
        how="left"
    )

    return df_train

def load_team_game_stats_for_season(season):
    """Load team game stats for a given season."""
    path = f"data/raw/team_game_stats_{season}.csv"
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)


def compute_team_context(df_team):
    """
    Compute team-level season metrics:
    - Pace
    - Offensive Rating (ORtg)
    - Defensive Rating (DRtg)
    """

    # Possessions formula (NBA standard)
    df_team["POSS"] = (
        df_team["FGA"]
        + 0.44 * df_team["FTA"]
        - df_team["OREB"]
        + df_team["TOV"]
    )

    # Pace = possessions per game
    team_pace = df_team["POSS"].mean()

    # ORtg = points per 100 possessions
    team_ortg = (df_team["PTS"] / df_team["POSS"]).mean() * 100

    # DRtg = opponent points per 100 possessions
    # Opponent stats are not directly available, so we approximate using PLUS_MINUS
    # DRtg ≈ ORtg - PLUS_MINUS impact
    team_drtg = team_ortg - df_team["PLUS_MINUS"].mean()

    return team_pace, team_ortg, team_drtg


def add_team_context_features(df_train):
    """
    Adds team context features (pace, ORtg, DRtg) for the CURRENT season.
    """

    seasons = sorted(df_train["SEASON_current"].unique())
    context_map = {}

    for season in seasons:
        df_team = load_team_game_stats_for_season(season)
        if df_team is None:
            continue

        # Compute team-level metrics
        team_pace, team_ortg, team_drtg = compute_team_context(df_team)

        # Map to every player in that season
        players_in_season = df_train[df_train["SEASON_current"] == season]["PLAYER_ID"].unique()

        for pid in players_in_season:
            context_map[(pid, season)] = {
                "TEAM_PACE_current": team_pace,
                "TEAM_ORtg_current": team_ortg,
                "TEAM_DRtg_current": team_drtg,
            }

    # Convert dictionary → DataFrame
    df_context = pd.DataFrame([
        {
            "PLAYER_ID": pid,
            "SEASON_current": season,
            **vals
        }
        for (pid, season), vals in context_map.items()
    ])

    # Merge into training dataset
    df_train = df_train.merge(
        df_context,
        on=["PLAYER_ID", "SEASON_current"],
        how="left"
    )

    return df_train

def add_usage_rate_features(df_train):
    """
    Adds Usage Rate (USG%) for the CURRENT season.
    USG = (FGA + 0.44*FTA + TOV) / Team Possessions
    """

    seasons = sorted(df_train["SEASON_current"].unique())
    usg_map = {}

    for season in seasons:
        # Load player game logs
        df_logs = load_game_logs_for_season(season)
        if df_logs is None:
            continue

        # Load team game stats
        df_team = load_team_game_stats_for_season(season)
        if df_team is None:
            continue

        # Compute team possessions for the season
        df_team["TEAM_POSS"] = (
            df_team["FGA"]
            + 0.44 * df_team["FTA"]
            - df_team["OREB"]
            + df_team["TOV"]
        )

        team_possessions = df_team["TEAM_POSS"].mean()

        # Compute usage per player
        for player_id in df_logs["PLAYER_ID"].unique():
            df_p = df_logs[df_logs["PLAYER_ID"] == player_id]

            if len(df_p) < 5:
                continue

            # Season totals
            fga = df_p["FGA"].sum()
            fta = df_p["FTA"].sum()
            tov = df_p["TOV"].sum()

            usg = (fga + 0.44 * fta + tov) / team_possessions

            usg_map[(player_id, season)] = {
                "USG_current": usg
            }

    # Convert dictionary → DataFrame
    df_usg = pd.DataFrame([
        {
            "PLAYER_ID": pid,
            "SEASON_current": season,
            **vals
        }
        for (pid, season), vals in usg_map.items()
    ])

    # Merge into training dataset
    df_train = df_train.merge(
        df_usg,
        on=["PLAYER_ID", "SEASON_current"],
        how="left"
    )

    return df_train

def add_ts_features(df_train):
    """
    Adds True Shooting Percentage (TS%) for the CURRENT season.
    TS = PTS / (2 * (FGA + 0.44 * FTA))
    """

    seasons = sorted(df_train["SEASON_current"].unique())
    ts_map = {}

    for season in seasons:
        df_logs = load_game_logs_for_season(season)
        if df_logs is None:
            continue

        for player_id in df_logs["PLAYER_ID"].unique():
            df_p = df_logs[df_logs["PLAYER_ID"] == player_id]

            if len(df_p) < 5:
                continue

            # Season totals
            pts = df_p["PTS"].sum()
            fga = df_p["FGA"].sum()
            fta = df_p["FTA"].sum()

            denom = (2 * (fga + 0.44 * fta))
            if denom == 0:
                ts = None
            else:
                ts = pts / denom

            ts_map[(player_id, season)] = {
                "TS_PCT_current": ts
            }

    # Convert dictionary → DataFrame
    df_ts = pd.DataFrame([
        {
            "PLAYER_ID": pid,
            "SEASON_current": season,
            **vals
        }
        for (pid, season), vals in ts_map.items()
    ])

    # Merge into training dataset
    df_train = df_train.merge(
        df_ts,
        on=["PLAYER_ID", "SEASON_current"],
        how="left"
    )

    return df_train

def load_rookie_data():
    """Load rookies.csv which contains draft information."""
    path = "data/raw/rookies.csv"
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)


def add_draft_features(df_train):
    """
    Adds draft features:
    - OVERALL_PICK
    - ROUND_PICK
    - ROUND_NUMBER
    - ROOKIE_FLAG
    """

    df_rookies = load_rookie_data()
    if df_rookies is None:
        return df_train

    # Keep only relevant columns
    df_rookies = df_rookies[
        ["PERSON_ID", "SEASON", "ROUND_NUMBER", "ROUND_PICK", "OVERALL_PICK"]
    ].rename(columns={"PERSON_ID": "PLAYER_ID"})

    # Merge draft info into training dataset
    df_train = df_train.merge(
        df_rookies,
        on="PLAYER_ID",
        how="left",
        suffixes=("", "_draft")
    )

    # Compute rookie flag
    df_train["ROOKIE_FLAG"] = (
        df_train["SEASON_current"] == df_train["SEASON"]
    ).astype(int)

    return df_train

def add_age_curve_features(df_train):
    """
    Adds age curve features:
    - AGE_SQUARED_current
    - AGE_BUCKET_current
    - AGE_DELTA_next
    """

    # Non-linear age curve
    df_train["AGE_SQUARED_current"] = df_train["AGE_current"] ** 2

    # Age delta (how much older the player gets next season)
    df_train["AGE_DELTA_next"] = df_train["AGE_next"] - df_train["AGE_current"]

    # Age buckets
    def age_bucket(age):
        if pd.isna(age):
            return None
        if age <= 23:
            return "young"
        elif age <= 26:
            return "developing"
        elif age <= 30:
            return "prime"
        elif age <= 34:
            return "veteran"
        else:
            return "old"

    df_train["AGE_BUCKET_current"] = df_train["AGE_current"].apply(age_bucket)

    return df_train

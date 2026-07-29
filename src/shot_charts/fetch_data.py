from nba_api.stats.endpoints import shotchartdetail
import pandas as pd
from pathlib import Path

def get_player_shots(player_id: int, season: str, season_type: str = "Regular Season") -> pd.DataFrame:
    sc = shotchartdetail.ShotChartDetail(
        team_id=0,
        player_id=player_id,
        season_type_all_star=season_type,
        season_nullable=season,
        context_measure_simple="FGA"
    )
    df = sc.get_data_frames()[0]
    return df

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SHOTS_DIR = PROJECT_ROOT / "data" / "shots"


def get_player_shots_local(player_id: int, season: str, season_type: str) -> pd.DataFrame:
    """
    Load shot data for a player from local CSVs in data/shots/{season}/{regular|playoffs}/{player_id}.csv

    season: e.g. "2013-14"
    season_type: "Regular Season" or "Playoffs"
    """

    # Map season type to folder name
    if season_type == "Regular Season":
        type_folder = "regular"
    elif season_type == "Playoffs":
        type_folder = "playoffs"
    else:
        raise ValueError(f"Unknown season_type: {season_type}")

    season_folder = SHOTS_DIR / season / type_folder
    csv_path = season_folder / f"{player_id}.csv"

    if not csv_path.exists():
        # No data for this player/season/type
        return pd.DataFrame()

    df = pd.read_csv(csv_path)

    # Optional: ensure key columns exist
    required_cols = [
        "GAME_ID", "GAME_EVENT_ID", "PLAYER_ID", "PLAYER_NAME",
        "TEAM_ID", "TEAM_NAME", "PERIOD",
        "MINUTES_REMAINING", "SECONDS_REMAINING",
        "EVENT_TYPE", "ACTION_TYPE", "SHOT_TYPE",
        "SHOT_ZONE_BASIC", "SHOT_ZONE_AREA", "SHOT_ZONE_RANGE",
        "SHOT_DISTANCE", "LOC_X", "LOC_Y",
        "SHOT_ATTEMPTED_FLAG", "SHOT_MADE_FLAG",
        "GAME_DATE", "HTM", "VTM"
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Shot CSV missing columns: {missing} in {csv_path}")

    return df
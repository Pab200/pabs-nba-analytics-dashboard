from nba_api.stats.endpoints import shotchartdetail
import pandas as pd

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
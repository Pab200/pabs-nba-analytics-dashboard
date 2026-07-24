def is_modern_season(season_str):
    return int(season_str.split("-")[0]) >= 1996

def is_accurate_data_season(season_str):
    return int(season_str.split("-")[0]) >= 2010

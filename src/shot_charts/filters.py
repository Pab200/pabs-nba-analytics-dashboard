import pandas as pd

# -----------------------------
# Zone Filters
# -----------------------------

def filter_zone_basic(df: pd.DataFrame, zone: str) -> pd.DataFrame:
    """
    Filters by SHOT_ZONE_BASIC.
    Examples:
        'Restricted Area'
        'Mid-Range'
        'Above the Break 3'
        'Left Corner 3'
        'Right Corner 3'
    """
    return df[df["SHOT_ZONE_BASIC"] == zone]

def filter_zone_area(df: pd.DataFrame, area: str) -> pd.DataFrame:
    """
    Filters by SHOT_ZONE_AREA.
    Examples:
        'Center(C)'
        'Left Side(L)'
        'Right Side(R)'
    """
    return df[df["SHOT_ZONE_AREA"] == area]

def filter_zone_range(df: pd.DataFrame, zone_range: str) -> pd.DataFrame:
    """
    Filters by SHOT_ZONE_RANGE.
    Examples:
        'Less Than 8 ft.'
        '8-16 ft.'
        '16-24 ft.'
        '24+ ft.'
    """
    return df[df["SHOT_ZONE_RANGE"] == zone_range]

# -----------------------------
# Shot Type Filters
# -----------------------------

def filter_shot_type(df: pd.DataFrame, shot_type: str) -> pd.DataFrame:
    """
    Filters by SHOT_TYPE.
    Examples:
        'Jump Shot'
        'Layup Shot'
        'Dunk Shot'
        'Hook Shot'
        'Tip Shot'
    """
    return df[df["SHOT_TYPE"] == shot_type]

# -----------------------------
# Distance Filters
# -----------------------------

def filter_distance_min(df: pd.DataFrame, min_dist: float) -> pd.DataFrame:
    return df[df["SHOT_DISTANCE"] >= min_dist]

def filter_distance_max(df: pd.DataFrame, max_dist: float) -> pd.DataFrame:
    return df[df["SHOT_DISTANCE"] <= max_dist]

def filter_distance_range(df: pd.DataFrame, min_dist: float, max_dist: float) -> pd.DataFrame:
    return df[(df["SHOT_DISTANCE"] >= min_dist) & (df["SHOT_DISTANCE"] <= max_dist)]

# -----------------------------
# Made / Missed Filters
# -----------------------------

def filter_made(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["SHOT_MADE_FLAG"] == 1]

def filter_missed(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["SHOT_MADE_FLAG"] == 0]

# -----------------------------
# Period Filters
# -----------------------------

def filter_period(df: pd.DataFrame, period: int) -> pd.DataFrame:
    return df[df["PERIOD"] == period]

# -----------------------------
# Team Filters
# -----------------------------

def filter_team(df: pd.DataFrame, team_name: str) -> pd.DataFrame:
    return df[df["TEAM_NAME"] == team_name]

# -----------------------------
# Action Filters
# -----------------------------

def filter_action_type(df: pd.DataFrame, action_type: str) -> pd.DataFrame:
    return df[df["ACTION_TYPE"] == action_type]

# -----------------------------
# Composite Filters
# -----------------------------

def apply_filters(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """
    Apply multiple filters at once.
    Example:
        apply_filters(
            df,
            zone_basic='Mid-Range',
            shot_type='Jump Shot',
            min_dist=10,
            max_dist=20,
            made=True,
            period=3
        )
    """

    out = df.copy()

    if "zone_basic" in kwargs:
        out = filter_zone_basic(out, kwargs["zone_basic"])

    if "zone_area" in kwargs:
        out = filter_zone_area(out, kwargs["zone_area"])

    if "zone_range" in kwargs:
        out = filter_zone_range(out, kwargs["zone_range"])

    if "shot_type" in kwargs:
        out = filter_shot_type(out, kwargs["shot_type"])

    if "min_dist" in kwargs:
        out = filter_distance_min(out, kwargs["min_dist"])

    if "max_dist" in kwargs:
        out = filter_distance_max(out, kwargs["max_dist"])

    if "dist_range" in kwargs:
        lo, hi = kwargs["dist_range"]
        out = filter_distance_range(out, lo, hi)

    if "made" in kwargs:
        out = filter_made(out) if kwargs["made"] else filter_missed(out)

    if "period" in kwargs:
        out = filter_period(out, kwargs["period"])

    if "team" in kwargs:
        out = filter_team(out, kwargs["team"])

    if "action_type" in kwargs:
        out = filter_action_type(out, kwargs["action_type"])

    return out
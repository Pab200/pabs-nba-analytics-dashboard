import pandas as pd

def clean_shot_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans raw nba_api shot chart data.
    Removes invalid coordinates and ensures numeric types.
    """

    df = df[(df["LOC_X"].notna()) & (df["LOC_Y"].notna())]

    df["LOC_X"] = pd.to_numeric(df["LOC_X"], errors="coerce")
    df["LOC_Y"] = pd.to_numeric(df["LOC_Y"], errors="coerce")
    df["SHOT_DISTANCE"] = pd.to_numeric(df["SHOT_DISTANCE"], errors="coerce")
    df["SHOT_MADE_FLAG"] = pd.to_numeric(df["SHOT_MADE_FLAG"], errors="coerce")
    df["PERIOD"] = pd.to_numeric(df["PERIOD"], errors="coerce")

    df = df.dropna(subset=["LOC_X", "LOC_Y", "SHOT_DISTANCE", "SHOT_MADE_FLAG", "PERIOD"])

    return df

def build_hover_text(df: pd.DataFrame) -> pd.Series:
    """
    Builds rich hover text for each shot.
    """

    return df.apply(
        lambda r: (
            f"{r['SHOT_TYPE']} • {r['SHOT_DISTANCE']} ft • "
            f"{r['SHOT_ZONE_BASIC']} • {r['SHOT_ZONE_RANGE']} • "
            f"Q{int(r['PERIOD'])}"
        ),
        axis=1
    )

def build_color_map(df: pd.DataFrame) -> pd.Series:
    """
    Maps made/missed shots to colors.
    """

    return df["SHOT_MADE_FLAG"].map({1: "green", 0: "red"})

def prepare_for_plotting(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full processing pipeline:
    - clean data
    - build hover text
    - build color mapping
    - return ready-to-plot DataFrame
    """

    df = clean_shot_data(df)

    df["hover"] = build_hover_text(df)
    df["color"] = build_color_map(df)

    return df
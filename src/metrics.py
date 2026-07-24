import pandas as pd

def add_true_shooting(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds True Shooting Percentage (TS%) to the DataFrame.
    TS% = PTS / (2 * (FGA + 0.44 * FTA))
    """
    if {"PTS", "FGA", "FTA"}.issubset(df.columns):
        df["TS_PCT"] = df["PTS"] / (2 * (df["FGA"] + 0.44 * df["FTA"]))
    return df


def add_effective_fg(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds Effective Field Goal Percentage (eFG%) to the DataFrame.
    eFG% = (FGM + 0.5 * FG3M) / FGA
    """
    if {"FGM", "FG3M", "FGA"}.issubset(df.columns):
        df["EFG_PCT"] = (df["FGM"] + 0.5 * df["FG3M"]) / df["FGA"]
    return df


def add_ast_tov(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds Assist-to-Turnover Ratio (AST/TOV).
    Handles division by zero safely.
    """
    if {"AST", "TOV"}.issubset(df.columns):
        df["AST_TOV"] = df["AST"] / df["TOV"].replace(0, pd.NA)
    return df


def add_advanced_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds all advanced metrics to the DataFrame.
    This is the main function your pages should call.
    """
    df = add_true_shooting(df)
    df = add_effective_fg(df)
    df = add_ast_tov(df)
    return df

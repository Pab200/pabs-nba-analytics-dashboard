import sqlite3
import pandas as pd
from contextlib import contextmanager

DB_PATH = "nba.db"

@contextmanager
def get_connection():
    """
    Context manager that yields a SQLite connection and ensures it closes cleanly.
    Usage:
        with get_connection() as conn:
            ...
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def run_query(sql: str, params: tuple = None) -> pd.DataFrame:
    """
    Run a SQL query and return a pandas DataFrame.
    Supports parameterized queries via params tuple.
    Example:
        run_query("SELECT * FROM season_stats WHERE SEASON = ?", ("2025-26",))
    """
    with get_connection() as conn:
        if params:
            return pd.read_sql_query(sql, conn, params=params)
        return pd.read_sql_query(sql, conn)

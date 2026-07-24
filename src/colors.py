"""
Team color definitions for NBA franchises.
Primary colors = main brand color
Secondary colors = accent color (used for borders, outlines, highlights)
"""

# ------------------------------------------------------------
# PRIMARY TEAM COLORS
# ------------------------------------------------------------
TEAM_COLORS = {
    "ATL": "#E13A3E",
    "BOS": "#007A33",
    "CLE": "#860038",
    "NOP": "#0C2340",
    "CHI": "#CE1141",
    "DAL": "#00538C",
    "DEN": "#0E2240",
    "GSW": "#1D428A",
    "HOU": "#CE1141",
    "LAC": "#1D428A",
    "LAL": "#552583",
    "MIA": "#98002E",
    "MIL": "#00471B",
    "MIN": "#0C2340",
    "BKN": "#000000",
    "NYK": "#006BB6",
    "ORL": "#0077C0",
    "IND": "#002D62",
    "PHI": "#006BB6",
    "PHX": "#1D1160",
    "POR": "#C8102E",
    "SAC": "#5B2C81",
    "SAS": "#000000",
    "OKC": "#007AC1",
    "TOR": "#CE1141",
    "UTA": "#F9A01B",
    "MEM": "#5D76A9",
    "WAS": "#002B5C",
    "DET": "#C8102E",
    "CHA": "#008CA8",
    "NJN": "#C8102E",
    "SEA": "#00653A",
    "NOH": "#008CA8",
    "VAN": "#00B2A9",
    "CHH": "#008CA8",
    "NOK": "#008CA8",
    "WSB": "#002B5C",
}

# ------------------------------------------------------------
# SECONDARY TEAM COLORS
# ------------------------------------------------------------
SEC_TEAM_COLORS = {
    "ATL": "#000000",
    "BOS": "#BA9653",
    "CLE": "#041E42",
    "NOP": "#85714D",
    "CHI": "#000000",
    "DAL": "#002B5E",
    "DEN": "#FEC524",
    "GSW": "#FFC72C",
    "HOU": "#000000",
    "LAC": "#C8102E",
    "LAL": "#FDB927",
    "MIA": "#000000",
    "MIL": "#EEE1C6",
    "MIN": "#78BE20",
    "BKN": "#FFFFFF",
    "NYK": "#F58426",
    "ORL": "#000000",
    "IND": "#FDBB30",
    "PHI": "#ED174C",
    "PHX": "#E56020",
    "POR": "#000000",
    "SAC": "#707272",
    "SAS": "#C4CED4",
    "OKC": "#F05133",
    "TOR": "#000000",
    "UTA": "#000000",
    "MEM": "#121F32",
    "WAS": "#E31837",
    "DET": "#1D42BA",
    "CHA": "#1D1160",
    "NJN": "#003DA5",
    "SEA": "#FFC200",
    "NOH": "#1D1160",
    "VAN": "#E43C40",
    "CHH": "#1D1160",
    "NOK": "#1D1160",
    "WSB": "#E31837",
}

# ------------------------------------------------------------
# SAFE HELPERS
# ------------------------------------------------------------
DEFAULT_PRIMARY = "#888888"
DEFAULT_SECONDARY = "#AAAAAA"

def get_primary(team: str) -> str:
    """Return primary team color or safe default."""
    return TEAM_COLORS.get(team, DEFAULT_PRIMARY)

def get_secondary(team: str) -> str:
    """Return secondary team color or safe default."""
    return SEC_TEAM_COLORS.get(team, DEFAULT_SECONDARY)

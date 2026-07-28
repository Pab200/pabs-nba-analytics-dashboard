import plotly.graph_objects as go
import pandas as pd
from src.shot_charts.court import draw_court

def plot_hexbin(df, team_abbr: str | None = None):
    """
    Hex-style visualization: hexagon markers on a fixed grid, size by frequency.
    Medium size (Hex Option 2).
    """

    fig = draw_court(team_abbr)

    bin_size = 30  # grid spacing
    df["x_bin"] = (df["LOC_X"] / bin_size).round() * bin_size
    df["y_bin"] = (df["LOC_Y"] / bin_size).round() * bin_size

    grouped = (
        df.groupby(["x_bin", "y_bin"])
        .size()
        .reset_index(name="count")
    )

    max_count = grouped["count"].max()

    # Size scaling: medium range to avoid crazy overlap
    grouped["size"] = grouped["count"] / max_count * 24 + 8  # 8–32

    colorscale = [
        [0.0, "#deebf7"],
        [0.3, "#9ecae1"],
        [0.6, "#3182bd"],
        [1.0, "#08519c"],
    ]

    fig.add_trace(go.Scatter(
        x=grouped["x_bin"],
        y=grouped["y_bin"],
        mode="markers",
        marker=dict(
            symbol="hexagon",
            size=grouped["size"],
            color=grouped["count"],
            colorscale=colorscale,
            showscale=True,
            line=dict(width=1, color="#ffffff"),
            opacity=0.9
        ),
        hovertemplate="Attempts: %{marker.color}<extra></extra>"
    ))

    fig.update_layout(
        hoverlabel=dict(
            bgcolor="rgba(30,30,30,0.9)",
            font_size=14,
            font_color="white",
            align="left"
        )
    )

    return fig
import plotly.graph_objects as go
from src.shot_charts.court import draw_court

def plot_heatmap(df, team_abbr: str | None = None):
    """
    Creates a shot density heatmap using LOC_X and LOC_Y,
    using contour-style 'geographic' heatmap.
    """

    fig = draw_court(team_abbr)

    fig.add_trace(go.Histogram2dContour(
        x=df["LOC_X"],
        y=df["LOC_Y"],
        colorscale="Hot",
        reversescale=True,
        showscale=True,
        contours=dict(
            coloring="heatmap"
        ),
        ncontours=20,
        opacity=0.7
    ))

    fig.add_trace(go.Scatter(
        x=df["LOC_X"],
        y=df["LOC_Y"],
        mode="markers",
        marker=dict(
            color="white",
            size=2,
            opacity=0.3
        ),
        hoverinfo="skip"
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
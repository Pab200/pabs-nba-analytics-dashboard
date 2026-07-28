import plotly.graph_objects as go
from src.shot_charts.court import draw_court

def plot_shots(df):
    """
    Plots a short chart on top of the NBA court.
    Expected columns:
    LOC_X, LOC_Y, SHOT_MADE_FLAG, SHOT_TYPE, SHOT_DISTANCE, PERIOD
    """

    fig = draw_court()

    # Use enriched hover text if available
    hover = df["hover"] if "hover" in df.columns else None
    colors = df["color"] if "color" in df.columns else df["SHOT_MADE_FLAG"].map({1: "green", 0: "red"})

    fig.add_trace(go.Scatter(
        x=df["LOC_X"],
        y=df["LOC_Y"],
        mode="markers",
        marker=dict(
            color=colors,
            size=7,
            opacity=0.85
        ),
        text=hover,
        hovertemplate="%{text}<extra></extra>"
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
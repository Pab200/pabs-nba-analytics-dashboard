import plotly.graph_objects as go
from src.shot_charts.court import draw_court
from src.colors import get_primary

def plot_shots(df, team_abbr: str | None = None):
    """
    Scatter shot chart:
    - O (green hollow circle) = make
    - X (red) = miss
    """
    fig = draw_court(team_abbr)

    primary = get_primary(team_abbr) if team_abbr else "#00A86B"
    miss_color = "#D62728"

    # --- COORDINATE ADJUSTMENTS ---
    # Shift Y by +52.5 to match baseline y=0 from NBA API hoop origin (0,0)
    # Invert X (-LOC_X) to match standard visual perspective
    df = df.copy()
    df["PLOT_X"] = -df["LOC_X"]
    df["PLOT_Y"] = df["LOC_Y"] + 52.5

    hover = df["hover"] if "hover" in df.columns else None

    made = df[df["SHOT_MADE_FLAG"] == 1]
    missed = df[df["SHOT_MADE_FLAG"] == 0]

    # Made shots: green hollow circles
    fig.add_trace(go.Scatter(
        x=made["PLOT_X"],
        y=made["PLOT_Y"],
        mode="markers",
        name="O Make",
        marker=dict(
            symbol="circle-open",
            line=dict(color=primary, width=2),
            size=10,
            opacity=0.9
        ),
        text=hover.loc[made.index] if hover is not None else None,
        hovertemplate="%{text}<extra></extra>"
    ))

    # Missed shots: red X
    fig.add_trace(go.Scatter(
        x=missed["PLOT_X"],
        y=missed["PLOT_Y"],
        mode="markers",
        name="X Miss",
        marker=dict(
            symbol="x",
            color=miss_color,
            size=10,
            opacity=0.9,
            line=dict(width=2, color=miss_color)
        ),
        text=hover.loc[missed.index] if hover is not None else None,
        hovertemplate="%{text}<extra></extra>"
    ))

    fig.update_layout(
        hoverlabel=dict(
            bgcolor="rgba(30,30,30,0.9)",
            font_size=14,
            font_color="white",
            align="left"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1.0
        )
    )

    return fig
import plotly.graph_objects as go

def draw_court(fig=None):
    """
    Draws an NBA half court using Plotly shapes.
    Returns a Plotly Figure object.
    """

    if fig is None:
        fig = go.Figure()

    # Outer boundary
    fig.add_shape(type="rect",
                  x0=-250, y0=47.5, x1=250, y1=422.5,
                  line=dict(color="black"))

    # Hoop
    fig.add_shape(type="circle",
                  x0=-7.5, y0=7.5, x1=7.5, y1=22.5,
                  line=dict(color="orange"))

    # Backboard
    fig.add_shape(type="rect",
                  x0=-30, y0=40, x1=30, y1=42,
                  line=dict(color="black"))

    # Paint (key)
    fig.add_shape(type="rect",
                  x0=-80, y0=-47.5, x1=80, y1=190,
                  line=dict(color="black"))

    #Free throw circle
    fig.add_shape(type="circle",
                  x0=-80, y0=110, x1=80, y1=270,
                  line=dict(color="black"))

    # Three-point arc
    fig.add_shape(
        type="path",
        path="M -220 0 A 220 220 0 0 1 220 0",
        line=dict(color="black")
    )

    # Remove axes
    fig.update_layout(
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        width=600,
        height=600
    )

    return fig
import plotly.graph_objects as go
import numpy as np

def draw_court(team_abbr: str | None = None):
    fig = go.Figure()

    # Half-court bounds: x from -250 to 250 (50ft), y from 0 to 470 (47ft)
    fig.update_layout(
        xaxis=dict(range=[-260, 260], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(range=[-10, 480], showgrid=False, zeroline=False, visible=False),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        width=600,
        height=560
    )

    shapes = []

    # --- 1. OUTER HALF-COURT BOUNDARY (47ft x 50ft) ---
    shapes.append(dict(
        type="rect",
        x0=-250, y0=0,
        x1=250, y1=470,
        line=dict(color="#000000", width=3),
        fillcolor="rgba(0,0,0,0)"
    ))

    # --- 2. THE PAINT / KEY (16ft wide x 19ft deep) ---
    shapes.append(dict(
        type="rect",
        x0=-80, y0=0,
        x1=80, y1=190,
        line=dict(color="#000000", width=3),
        fillcolor="rgba(0,0,0,0)"  # Change to a hex code if you want a filled paint area
    ))

    # --- 3. 3-POINT LINE ---
    hoop_x = 0
    hoop_y = 52.5  # Rim center is 5.25 ft (52.5 units) from baseline
    radius = 237.5  # 23.75 ft

    # Corner 3 lines (22 ft from center x=0, running 14 ft long from y=0 to y=140)
    shapes.append(dict(
        type="line", x0=-220, y0=0, x1=-220, y1=140,
        line=dict(color="#000000", width=3)
    ))
    shapes.append(dict(
        type="line", x0=220, y0=0, x1=220, y1=140,
        line=dict(color="#000000", width=3)
    ))

    # Arc connecting corner lines (x from -220 to 220)
    arc_x = np.linspace(-220, 220, 400)
    inside = radius**2 - (arc_x - hoop_x)**2
    inside[inside < 0] = 0
    arc_y = hoop_y + np.sqrt(inside)

    path_points = [f"{x:.2f},{y:.2f}" for x, y in zip(arc_x, arc_y)]
    arc_path = f"M {path_points[0]} L " + " L ".join(path_points[1:])

    shapes.append(dict(
        type="path",
        path=arc_path,
        line=dict(color="#000000", width=3)
    ))

    # --- 4. BACKBOARD & HOOP (Lighter line thickness) ---
    # Backboard: 4 ft (40 units) from baseline, 6 ft (60 units) wide
    shapes.append(dict(
        type="line",
        x0=-30, y0=40,
        x1=30, y1=40,
        line=dict(color="#000000", width=1.5)
    ))

    # Hoop: 18 inch diameter (radius 7.5 units), center at (0, 52.5)
    shapes.append(dict(
        type="circle",
        x0=-7.5, y0=45,
        x1=7.5, y1=60,
        line=dict(color="#000000", width=1.5),
        fillcolor="rgba(0,0,0,0)"
    ))

    fig.update_layout(shapes=shapes)

    return fig
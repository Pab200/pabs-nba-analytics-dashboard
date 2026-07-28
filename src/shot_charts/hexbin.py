import plotly.graph_objects as go
import numpy as np
from src.shot_charts.court import draw_court

def plot_hexbin(df, gridsize=30):
    """
    Creates a hexbin shot chart using numpy histogram2d.
    """

    x = df["LOC_X"].values
    y = df["LOC_Y"].values

    counts, xedges, yedges = np.histogram2d(x, y, bins=gridsize)

    xcenters = (xedges[:-1] + xedges[1:]) / 2
    ycenters = (yedges[:-1] + yedges[1:]) / 2

    fig = draw_court()

    fig.add_trace(go.Histogram2d(
        x=x,
        y=y,
        colorscale="Viridis",
        nbinsx=gridsize,
        nbinsy=gridsize,
        showscale=True,
        opacity=0.85
    ))

    return fig
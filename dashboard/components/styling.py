import streamlit as st

# ------------------------------------------------------------
# GLOBAL CSS
# ------------------------------------------------------------
GLOBAL_CSS = """
<style>

    /* Sidebar background */
    [data-testid="stSidebar"] {
        background-color: #1E1E1E;
    }

    /* Make ALL sidebar text white */
    [data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Keep selectbox VALUE readable */
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] * {
        color: black !important;
    }

    /* Custom sidebar title */
    .sidebar-title {
        color: white !important;
        font-size: 28px;
        font-weight: bold;
        margin-top: 0px;
        margin-bottom: 15px;
    }

    /* Page title */
    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: bold;
        margin-bottom: 20px;
    }

</style>
"""


def load_css():
    """Inject global CSS into the Streamlit app."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def set_sidebar_title(text: str):
    """
    Render a custom sidebar title that *can* be styled with CSS.
    Streamlit's built-in st.sidebar.title() cannot be styled reliably.
    """
    st.sidebar.markdown(
        f"<h2 class='sidebar-title'>{text}</h2>",
        unsafe_allow_html=True
    )


# ------------------------------------------------------------
# TABLE STYLING
# ------------------------------------------------------------
def color_team_table(df, primary, secondary):
    """
    Apply team color styling to a DataFrame.
    Used for player/team summary tables.
    """
    return df.style.set_properties(
        **{
            "background-color": secondary + "30",
            "color": primary,
            "border-color": primary
        }
    ).set_table_styles([
        {
            "selector": "th",
            "props": [
                ("background-color", primary),
                ("color", "white")
            ]
        }
    ])
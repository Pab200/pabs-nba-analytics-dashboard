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

    /* Sidebar title */
    [data-testid="stSidebarContent"] h2 {
        color: white !important;
    }

    /* Sidebar radio label */
    [data-testid="stSidebar"] .stRadio > label {
        color: white !important;
    }

    /* Sidebar radio options */
    [data-testid="stSidebar"] .stRadio div {
        color: white !important;
    }

    /* Sidebar selectbox label */
    [data-testid="stSidebar"] label {
        color: white !important;
    }

    /* Selectbox selected value */
    div[data-testid="stSelectbox"] > div > div > div {
        color: black !important;
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

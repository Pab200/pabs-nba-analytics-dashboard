import streamlit as st

def render(selected_season, seasons):
    st.header("ℹ️ About This Project")

    st.write("""
        This NBA Analytics Dashboard was built to explore multiple seasons using real SQL queries, Python, and Streamlit.
                
        **Technologies Used**
        - SQLite
        - Pandas
        - Matplotlib
        - Streamlit
                
        **Future Ideas**
        - Player Images
        - Player Projections
        - Fantasy Basketball
        - Interactive Shot Charts
        - Team Comparison & Filters
    """)
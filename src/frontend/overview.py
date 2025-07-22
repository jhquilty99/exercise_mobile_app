import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from backend.overview_statistics import calculate_filtered_metrics

def render_overview_page(df):
    """
    Renders the Overview page content.
    Provides a high-level summary of the fitness journey.
    """
    st.header("📊 Overview")
    st.write("Welcome to your workout dashboard! This section provides a high-level summary of your fitness journey.")
    st.info("Select a section from the sidebar to explore detailed analytics.")
    
    # Timeframe filter
    st.subheader("Time Period Filter")
    timeframe_options = [
        "Last 7 days",
        "Last 30 days", 
        "Last 3 months",
        "Last 6 months",
        "Last year",
        "All time"
    ]
    
    selected_timeframe = st.selectbox(
        "Select time period for metrics:",
        timeframe_options,
        index=5  # Default to "All time"
    )
    
    # Calculate filtered metrics based on timeframe
    filtered_workouts, filtered_exercises = calculate_filtered_metrics(
        df, selected_timeframe
    )
    
    # Key metrics displayed in a clean grid layout
    st.subheader("Quick Stats")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(label="Total Workouts", value=filtered_workouts)
    
    with col2:
        st.metric(label="Total Exercises", value=filtered_exercises)

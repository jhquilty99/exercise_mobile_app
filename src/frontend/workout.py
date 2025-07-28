import streamlit as st
import pandas as pd
from datetime import datetime
import calendar
from backend.workout_statistics import calculate_workout_streak, create_workout_frequency_graph, create_workout_calendar


def render_workout_analysis_page(df: pd.DataFrame):
    """
    Renders the Workout Analysis page content.
    Implements FE-014: Workout Analysis Tab
    """
    # Welcoming header with emoji
    st.header("📊 Workout Analysis")
    
    # Brief description
    st.write("Welcome to your workout analysis dashboard! This page helps you evaluate your workout regiment over time with detailed insights into your fitness patterns.")
    
    # Calculate and display current streak
    current_streak = calculate_workout_streak(df)
    
    st.subheader("Current Streak")
    st.metric(
        label="🔥 Current Streak",
        value=f"{current_streak} days"
    )
    
    # Workout frequency over time graph
    st.subheader("Workout Frequency Over Time")
    frequency_fig = create_workout_frequency_graph(df)
    st.plotly_chart(frequency_fig, use_container_width=True)
    
    # Calendar section
    st.subheader("Workout Calendar")
    
    # Year selector
    current_year = datetime.now().year
    selected_year = st.selectbox(
        "Select Year",
        range(current_year - 2, current_year + 1),
        index=2  # Default to current year
    )
    
    # Display calendar
    calendar_fig = create_workout_calendar(df, year=selected_year)
    st.plotly_chart(calendar_fig, use_container_width=True)

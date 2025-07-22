import streamlit as st
import pandas as pd
from backend.all_exercise_statistics import analyze_all_exercises

def render_all_exercise_analysis_page(df):
    """
    Renders the All Exercise Analysis page content.
    Provides detailed analysis of all exercises against one another.
    """
    # Welcoming header with emoji
    st.header("📊 All Exercise Analysis")
    
    # Brief description
    st.write("This tab allows you to analyze all exercises against one another using different key metrics and timeframes.")
    
    # Key Metrics selection
    st.subheader("Key Metrics")
    key_metrics = [
        "Max Volume",
        "Max Weight", 
        "Average Reps",
        "Count"
    ]
    
    selected_metric = st.selectbox(
        "Select key metric to analyze:",
        key_metrics,
        index=0  # Default to "Max Volume"
    )
    
    # Timeframe filters
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
        "Select time period for analysis:",
        timeframe_options,
        index=5  # Default to "All time"
    )
    
    # Analyze data using backend function
    try:
        analysis_results = analyze_all_exercises(
            df=df,
            key_metric=selected_metric,
            timeframe=selected_timeframe
        )
        
        # Display results table
        st.subheader(f"Exercise Analysis: {selected_metric} over ({selected_timeframe})")
        
        if not analysis_results.empty:
            # Create a clean display DataFrame
            display_df = analysis_results.copy()
            display_df.columns = ['Rank', 'Exercise Name', selected_metric]
            
            # Display the table
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
        else:
            st.warning("No data available for the selected timeframe and metric combination.")
            
    except Exception as e:
        st.error(f"Error analyzing exercise data: {str(e)}")
        st.info("Please check that your data contains the required columns for analysis.")

import streamlit as st
import pandas as pd
import plotly.express as px
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
            
            # Create bar chart for top 10 exercises
            st.subheader("📈 Top 10 Exercises Visualization")
            
            # Get top 10 exercises
            top_10_df = analysis_results.head(10).copy()
            
            # Create the bar chart
            fig = px.bar(
                top_10_df,
                x='detailed_exercise_name',
                y=top_10_df.columns[2],  # The metric column (3rd column)
                title=f"Top 10 Exercises by {selected_metric} ({selected_timeframe})",
                labels={
                    'detailed_exercise_name': 'Exercise Name',
                    top_10_df.columns[2]: selected_metric
                },
                color='rank',
                color_continuous_scale='viridis',
                text=top_10_df.columns[2]  # Show values on bars
            )
            
            # Customize the chart
            fig.update_layout(
                xaxis_title="Exercise Name",
                yaxis_title=selected_metric,
                showlegend=False,
                height=500
            )
            
            # Rotate x-axis labels for better readability
            fig.update_xaxes(tickangle=45)
            
            # Display the chart
            st.plotly_chart(fig, use_container_width=True)

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

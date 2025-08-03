import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from backend.specific_exercise_analysis import analyze_specific_exercise


@st.cache_data
def get_exercise_names(df: pd.DataFrame) -> list:
    """
    Get list of unique exercise names from the dataset.
    Cached to avoid repeated computation.
    """
    if df.empty or 'detailed_exercise_name' not in df.columns:
        return []
    
    return sorted(df['detailed_exercise_name'].unique().tolist())


@st.cache_data
def get_exercise_analysis(exercise_name: str, df: pd.DataFrame) -> dict:
    """
    Get analysis results for a specific exercise.
    Cached to only call backend again if exercise name changes.
    """
    return analyze_specific_exercise(exercise_name, df)


def create_progress_graph(filtered_data: pd.DataFrame, metric: str) -> go.Figure:
    """
    Create a line graph showing progress over time for a specific metric.
    
    Args:
        filtered_data: DataFrame with exercise data
        metric: Metric to plot ('volume', 'weight', 'reps', 'sets')
        
    Returns:
        Plotly figure object
    """
    if filtered_data.empty:
        return go.Figure()
    
    # Ensure data is sorted by date
    data = filtered_data.sort_values('workout_date').copy()
    
    # Create the line graph
    fig = go.Figure()
    
    # Add line with dots
    fig.add_trace(
        go.Scatter(
            x=data['workout_date'],
            y=data[metric],
            mode='lines+markers',
            line=dict(color='green', width=2),
            marker=dict(size=6, color='green'),
            name=f'{metric.title()} Over Time'
        )
    )
    
    # Update layout
    fig.update_layout(
        title=f'{metric.title()} Progress Over Time',
        xaxis_title='Date',
        yaxis_title=metric.title(),
        hovermode='x unified',
        showlegend=False
    )
    
    return fig


def render_specific_exercise_analysis_page(df: pd.DataFrame):
    """
    Renders the Specific Exercise Analysis page content.
    Implements FE-013: Specific Exercise Analysis Tab
    """
    # Welcoming header with emoji
    st.header("📊 Specific Exercise Analysis")
    
    # Brief description
    st.write("This page shows your progress for particular exercises over time. Select an exercise below to see detailed performance metrics and trends.")
    
    # Get available exercise names
    exercise_names = get_exercise_names(df)
    
    if not exercise_names:
        st.warning("No exercise data found. Please ensure your dataset contains exercise information.")
        return
    
    # Exercise filter
    st.subheader("Select Exercise")
    selected_exercise = st.selectbox(
        "Choose an exercise to analyze:",
        exercise_names,
        index=0
    )
    
    if selected_exercise:
        # Get analysis results (cached)
        analysis_result = get_exercise_analysis(selected_exercise, df)
        
        if not analysis_result['exercise_found']:
            st.warning(f"No data found for exercise: {selected_exercise}")
            return
        
        filtered_data = analysis_result['filtered_data']
        max_statistics = analysis_result['max_statistics']
        
        # Metric selection for graph
        st.subheader("Progress Graph")
        metric_options = {
            'Volume': 'volume',
            'Weight': 'weight', 
            'Reps': 'reps',
            'Sets': 'sets'
        }
        
        selected_metric_display = st.selectbox(
            "Select metric to display:",
            list(metric_options.keys()),
            index=0
        )
        
        selected_metric = metric_options[selected_metric_display]
        
        # Create and display the progress graph
        if not filtered_data.empty and selected_metric in filtered_data.columns:
            fig = create_progress_graph(filtered_data, selected_metric)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No {selected_metric_display.lower()} data available for this exercise.")
        
        # Display statistics
        st.subheader("Maximum Achievements")
        
        if max_statistics:
            # Create columns for better layout
            col1, col2 = st.columns(2)
            
            with col1:
                if 'max_volume' in max_statistics:
                    st.metric(
                        label="🏋️ Max Volume",
                        value=f"{max_statistics['max_volume']['value']:.1f}",
                        help=f"Achieved on {max_statistics['max_volume']['date']}"
                    )
                
                if 'max_weight' in max_statistics:
                    st.metric(
                        label="💪 Max Weight",
                        value=f"{max_statistics['max_weight']['value']:.1f} lbs",
                        help=f"Achieved on {max_statistics['max_weight']['date']}"
                    )
            
            with col2:
                if 'max_reps' in max_statistics:
                    st.metric(
                        label="🔄 Max Reps",
                        value=f"{max_statistics['max_reps']['value']}",
                        help=f"Achieved on {max_statistics['max_reps']['date']}"
                    )
                
                if 'max_sets' in max_statistics:
                    st.metric(
                        label="📊 Max Sets",
                        value=f"{max_statistics['max_sets']['value']}",
                        help=f"Achieved on {max_statistics['max_sets']['date']}"
                    )
        else:
            st.info("No maximum statistics available for this exercise.")
        
        # Display summary information
        st.subheader("Exercise Summary")
        st.write(f"**Total Records:** {analysis_result['total_records']} workout sessions")
        st.write(f"**Date Range:** {filtered_data['workout_date'].min().strftime('%Y-%m-%d')} to {filtered_data['workout_date'].max().strftime('%Y-%m-%d')}")

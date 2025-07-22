from datetime import datetime, timedelta, date
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import calendar
from typing import Tuple

def calculate_workout_streak(df: pd.DataFrame) -> Tuple[int, str]:
    """
    Calculate the current workout streak and provide evaluation.
    
    Args:
        df: DataFrame with workout data
        
    Returns:
        Tuple of (current_streak, evaluation_message)
    """
    if df.empty or 'Workout Date' not in df.columns:
        return 0, "No workout data available"
    
    # Get unique workout dates and sort them
    workout_dates = pd.to_datetime(df['Workout Date']).dt.date.unique()
    workout_dates = sorted(workout_dates)
    
    if not workout_dates:
        return 0, "No workout data available"
    
    # Calculate current streak with logic that allows missing workouts every other day
    current_date = date.today()
    current_streak = 0
    
    # Find the latest workout date
    latest_workout_date = max(workout_dates)
    
    # If the latest workout is today or yesterday, calculate streak
    if latest_workout_date >= current_date - timedelta(days=1):
        # Start from the latest workout date and count backwards
        check_date = latest_workout_date
        streak_days = 0
        
        while check_date >= current_date - timedelta(days=30):  # Limit to reasonable range
            if check_date in workout_dates:
                streak_days += 1
                # Move back 1 day (allows missing every other day)
                check_date -= timedelta(days=1)
            else:
                # Check if we can skip a day (missing every other day logic)
                if check_date - timedelta(days=1) in workout_dates:
                    # We can skip this day and continue
                    check_date -= timedelta(days=1)
                else:
                    # Break the streak
                    break
        
        current_streak = streak_days
    
    return current_streak

def create_workout_frequency_graph(df: pd.DataFrame) -> go.Figure:
    """
    Create a graph showing workout frequency over time using 30-day rolling window.
    
    Args:
        df: DataFrame with workout data
        
    Returns:
        Plotly figure object
    """
    if df.empty or 'Workout Date' not in df.columns:
        # Create empty figure
        fig = go.Figure()
        fig.add_annotation(
            text="No workout data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Get unique workout dates
    df_copy = df.copy()
    df_copy['Workout Date'] = pd.to_datetime(df_copy['Workout Date'])
    unique_workout_dates = df_copy['Workout Date'].dt.date.unique()
    
    if len(unique_workout_dates) == 0:
        # Create empty figure
        fig = go.Figure()
        fig.add_annotation(
            text="No workout data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Create date range from earliest to latest workout date
    min_date = min(unique_workout_dates)
    max_date = max(unique_workout_dates)
    
    # Create a complete date range
    date_range = pd.date_range(start=min_date, end=max_date, freq='D')
    
    # Calculate 30-day rolling window of unique workout dates
    rolling_frequency = []
    dates_for_plot = []
    
    for i, current_date in enumerate(date_range):
        if i < 29:  # Need at least 30 days of data
            continue
            
        # Calculate the 30-day window ending at current_date
        window_start = current_date - timedelta(days=29)
        window_end = current_date
        
        # Count unique workout dates in the 30-day window
        workout_dates_in_window = [
            date for date in unique_workout_dates 
            if window_start.date() <= date <= window_end.date()
        ]
        
        rolling_frequency.append(len(workout_dates_in_window))
        dates_for_plot.append(current_date)
    
    # Create the line chart
    fig = px.line(
        x=dates_for_plot,
        y=rolling_frequency,
        title='Workout Frequency Over Time (30-Day Rolling Window)',
        labels={'x': 'Date', 'y': 'Number of Unique Workout Days'},
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Number of Unique Workout Days (30-day window)",
        hovermode='x unified',
        showlegend=False
    )
    
    return fig

def create_workout_calendar(df: pd.DataFrame, year: int = None, month: int = None) -> go.Figure:
    """
    Create a calendar visualization with workout dates highlighted.
    
    Args:
        df: DataFrame with workout data
        year: Year to display (defaults to current year)
        month: Month to display (defaults to current month)
        
    Returns:
        Plotly figure object
    """
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month
    
    # Get workout dates for the specified month
    workout_dates = set()
    if not df.empty and 'Workout Date' in df.columns:
        df_copy = df.copy()
        df_copy['Workout Date'] = pd.to_datetime(df_copy['Workout Date'])
        month_workouts = df_copy[
            (df_copy['Workout Date'].dt.year == year) & 
            (df_copy['Workout Date'].dt.month == month)
        ]
        workout_dates = set(month_workouts['Workout Date'].dt.day.tolist())
    
    # Create calendar data
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    # Prepare data for heatmap - create proper calendar grid
    calendar_data = []
    hover_text = []
    
    for week in cal:
        week_data = []
        week_hover = []
        for day in week:
            if day == 0:  # Empty day
                week_data.append(0)
                week_hover.append("")
            else:
                if day in workout_dates:
                    week_data.append(2)  # Workout day
                    week_hover.append(f"Day {day} (Workout!)")
                else:
                    week_data.append(1)  # Regular day
                    week_hover.append(f"Day {day}")
        calendar_data.append(week_data)
        hover_text.append(week_hover)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=calendar_data,
        colorscale=[[0, 'white'], [0.5, 'lightgray'], [1, 'green']],
        showscale=False,
        hoverinfo='text',
        text=hover_text,
        x=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        y=[f"Week {i+1}" for i in range(len(calendar_data))]
    ))
    
    fig.update_layout(
        title=f"{month_name} {year} - Workout Calendar",
        xaxis_title="",
        yaxis_title="",
        height=300,
        width=600
    )
    
    return fig
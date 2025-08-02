from datetime import datetime, timedelta, date
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import calendar
from plotly_calplot import calplot

def calculate_workout_streak(df: pd.DataFrame) -> int:
    """
    Calculate the latest workout streak and provide evaluation.
    
    Args:
        df: DataFrame with workout data
        
    Returns:
        Int of current_streak_days
    """
    # Handle empty or invalid input
    if df is None or df.empty:
        return 0
    
    # Check if workout_date column exists
    if 'workout_date' not in df.columns:
        return 0
    
    try:
        # Get unique workout dates and convert to set for faster lookups
        workout_dates = pd.to_datetime(df['workout_date']).dt.date.unique()
        workout_dates_set = set(workout_dates)
        workout_dates = sorted(workout_dates)
        
        if len(workout_dates) == 0:
            return 0
        
        # Find the longest streak ending at the most recent workout
        current_streak = 0
        latest_workout_date = max(workout_dates)
        
        # Start from the latest workout and count backwards
        check_date = latest_workout_date
        streak_start_date = latest_workout_date
        
        while check_date in workout_dates_set:
            streak_start_date = check_date
            # Move back 1 day
            check_date -= timedelta(days=1)
            
            # Allow missing every other day (alternating pattern)
            # If we can't find the previous day, check if we can skip it
            if check_date not in workout_dates_set:
                # Check if we can skip this day and continue with the day before
                skip_date = check_date - timedelta(days=1)
                if skip_date in workout_dates_set:
                    # We can skip this day and continue
                    check_date = skip_date
                else:
                    # Can't skip, so this breaks the streak
                    break
        
        # Calculate the total days in the streak (from start to end, including skipped days)
        if streak_start_date != latest_workout_date:
            # There was a streak, calculate the total days
            current_streak = (latest_workout_date - streak_start_date).days + 1
        else:
            # Single day workout
            current_streak = 1
        
        return current_streak
        
    except Exception as e:
        # Handle any errors gracefully
        return 0

def get_current_workout_streak(df: pd.DataFrame) -> int:
    """
    Evaluate if there is a current workout streak based on today's date.
    A current streak means the most recent workout was within the last 2 days.
    
    Args:
        df: DataFrame with workout data
        
    Returns:
        Int of current_streak_days
    """
    # Handle empty or invalid input
    if df is None or df.empty:
        return 0
    
    # Check if workout_date column exists
    if 'workout_date' not in df.columns:
        return 0
    
    try:
        # Get the current streak calculation
        streak_days = calculate_workout_streak(df)
        
        # Get unique workout dates and find the most recent
        workout_dates = pd.to_datetime(df['workout_date']).dt.date.unique()
        if len(workout_dates) == 0:
            return 0
        
        latest_workout_date = max(workout_dates)
        today = date.today()
        
        # Calculate days since the last workout
        days_since_last_workout = (today - latest_workout_date).days
        
        # Check if the streak is current (workout within last 2 days)
        if days_since_last_workout <= 2:
            return streak_days
        else:
            # No current streak - the last workout was too long ago
            return 0
        
    except Exception as e:
        # Handle any errors gracefully
        return 0

def create_workout_frequency_graph(df: pd.DataFrame) -> go.Figure:
    """
    Create a graph showing workout frequency over time using 30-day rolling window.
    
    Args:
        df: DataFrame with workout data
        
    Returns:
        Plotly figure object
    """
    if df.empty or 'workout_date' not in df.columns:
        # Create empty figure
        fig = go.Figure()
        fig.add_annotation(
            text="No workout data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    try:
        # Get unique workout dates
        df_copy = df.copy()
        df_copy['workout_date'] = pd.to_datetime(df_copy['workout_date'])
        unique_workout_dates = df_copy['workout_date'].dt.date.unique()
        
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
        
    except Exception as e:
        # Handle any errors gracefully
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error creating frequency graph: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig

def create_workout_calendar(df: pd.DataFrame, year: int = None) -> go.Figure:
    """
    Create a GitHub-style contributions graph showing workout activity for an entire year.
    
    Args:
        df: DataFrame with workout data
        year: Year to display (defaults to current year)
        
    Returns:
        Plotly figure object
    """
    try:
        df_copy = df.copy()
        
        # Use current year if not specified
        if year is None:
            year = datetime.now().year
        
        # Handle empty dataframe
        if df_copy.empty or 'workout_date' not in df_copy.columns:
            fig = go.Figure()
            fig.add_annotation(
                text="No workout data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        # Group by workout_date and count occurrences
        daily_counts = df_copy.groupby('workout_date').size().reset_index(name='value')
        
        # Filter for the specified year if data exists
        if not daily_counts.empty:
            daily_counts['workout_date'] = pd.to_datetime(daily_counts['workout_date'])
            daily_counts = daily_counts[daily_counts['workout_date'].dt.year == year]
        
        # Check if we have data for the specified year
        if daily_counts.empty:
            fig = go.Figure()
            fig.add_annotation(
                text=f"No workout data available for {year}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        # Create the calendar plot
        fig = calplot(daily_counts, x="workout_date", y="value")
        
        # Ensure we have a valid figure
        if fig is None or len(fig.data) == 0:
            fig = go.Figure()
            fig.add_annotation(
                text="No workout data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
        
        return fig
        
    except Exception as e:
        # Handle any errors gracefully
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error creating calendar: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
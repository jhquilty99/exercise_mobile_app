from datetime import datetime, timedelta
import pandas as pd

def calculate_filtered_metrics(df, timeframe):
    """
    Calculate filtered metrics based on the selected timeframe.
    Returns filtered workout count and exercise count.
    """    
    try:    
        # Calculate the cutoff date based on timeframe
        today = datetime.now()

        if timeframe == "All time":
            # For "All Time", return unfiltered results
            filtered_workouts = df['Workout Date'].nunique()
            filtered_exercises = len(df)
            return filtered_workouts, filtered_exercises
        elif timeframe == "Last 7 days":
            cutoff_date = today - timedelta(days=7)
        elif timeframe == "Last 30 days":
            cutoff_date = today - timedelta(days=30)
        elif timeframe == "Last 3 months":
            cutoff_date = today - timedelta(days=90)
        elif timeframe == "Last 6 months":
            cutoff_date = today - timedelta(days=180)
        elif timeframe == "Last year":
            cutoff_date = today - timedelta(days=365)
        
        # Filter data based on cutoff date
        filtered_df = df[df['Workout Date'] >= cutoff_date]
        
        # Calculate filtered metrics
        filtered_workouts = filtered_df['Workout Date'].nunique()
        filtered_exercises = len(filtered_df)
        
        return filtered_workouts, filtered_exercises
            
    except Exception as e:
        return 0, 0
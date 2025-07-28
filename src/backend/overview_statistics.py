from datetime import datetime, timedelta
import pandas as pd
from .filter import filter_dataframe_by_timeframe

def calculate_filtered_metrics(df, timeframe):
    """
    Calculate filtered metrics based on the selected timeframe.
    Returns filtered workout count and exercise count.
    """    
    try:    
        # Use the filter function to get filtered dataframe
        filtered_df = filter_dataframe_by_timeframe(df, timeframe)
        
        # Calculate filtered metrics
        filtered_workouts = filtered_df['workout_date'].nunique()
        filtered_exercises = len(filtered_df)
        
        return filtered_workouts, filtered_exercises
            
    except Exception as e:
        return 0, 0
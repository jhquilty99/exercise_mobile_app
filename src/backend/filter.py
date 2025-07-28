from datetime import datetime, timedelta
import pandas as pd

def filter_dataframe_by_timeframe(df, timeframe):
    """
    Filter dataframe based on the selected timeframe.
    
    Args:
        df (pd.DataFrame): The dataframe to filter
        timeframe (str): The timeframe to filter by ("All time", "Last 7 days", etc.)
    
    Returns:
        pd.DataFrame: Filtered dataframe based on the timeframe
    """
    try:
        # For "All Time", return unfiltered dataframe
        if timeframe == "All time":
            return df
        
        # Calculate the cutoff date based on timeframe
        today = datetime.now()
        
        if timeframe == "Last 7 days":
            cutoff_date = today - timedelta(days=7)
        elif timeframe == "Last 30 days":
            cutoff_date = today - timedelta(days=30)
        elif timeframe == "Last 3 months":
            cutoff_date = today - timedelta(days=90)
        elif timeframe == "Last 6 months":
            cutoff_date = today - timedelta(days=180)
        elif timeframe == "Last year":
            cutoff_date = today - timedelta(days=365)
        else:
            # If timeframe is not recognized, return unfiltered dataframe
            return df
        
        # Filter data based on cutoff date
        filtered_df = df[df['workout_date'] >= cutoff_date]
        
        return filtered_df
        
    except Exception as e:
        # Return empty dataframe with same columns if there's an error
        return pd.DataFrame(columns=df.columns)

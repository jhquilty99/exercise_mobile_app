"""
Summary Statistics Module

This module provides functions to calculate basic summary statistics
from workout data extracted by the extraction module.
"""

import pandas as pd
import logging

# Configure logging
logger = logging.getLogger(__name__)


def calculate_total_rows(df: pd.DataFrame) -> int:
    """
    Calculate the total number of rows in the workout dataframe.
    
    Args:
        df: DataFrame containing workout data from extraction module
        
    Returns:
        int: Total number of rows in the dataframe
        
    Raises:
        ValueError: If dataframe is None or empty
    """
    total_rows = len(df)
    logger.info(f"Total rows calculated: {total_rows}")
    return total_rows


def calculate_distinct_dates(df: pd.DataFrame) -> int:
    """
    Calculate the total number of distinct workout dates in the dataframe.
    
    Args:
        df: DataFrame containing workout data from extraction module
        
    Returns:
        int: Total number of distinct dates
        
    Raises:
        ValueError: If dataframe is None or missing 'Workout Date' column
    """
    # Calculate distinct dates
    distinct_dates = df['Workout Date'].dt.date.nunique()
    logger.info(f"Distinct dates calculated: {distinct_dates}")
    return distinct_dates
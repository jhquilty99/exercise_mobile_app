"""
Specific Exercise Analysis Module

This module provides functionality for analyzing individual exercise performance over time:
- Filter data by specific exercise name
- Calculate maximum statistics for selected exercises
- Handle cases where no data exists for selected exercises
"""

import logging
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


def analyze_specific_exercise(exercise_name: str, df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze individual exercise performance over time.
    
    This function implements BE-008 requirements:
    - Filter data by specific exercise name and return time series data
    - Calculate maximum statistics for the selected exercise:
        - Max Volume with date achieved
        - Max Weight with date achieved  
        - Max Reps with date achieved
        - Max Sets with date achieved
    - Handle cases where no data exists for the selected exercise
    
    Args:
        exercise_name: Name of the exercise to analyze
        df: Input DataFrame with workout data
        
    Returns:
        Dictionary containing:
        - 'filtered_data': DataFrame with data for the specific exercise
        - 'max_statistics': Dictionary with max values and their dates
        - 'exercise_found': Boolean indicating if exercise exists in data
        - 'total_records': Number of records found for the exercise
    """
    
    try:
        # Validate input parameters
        if not isinstance(exercise_name, str) or not exercise_name.strip():
            error_msg = "exercise_name must be a non-empty string"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if not isinstance(df, pd.DataFrame):
            error_msg = "df must be a pandas DataFrame"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if df.empty:
            logger.warning("Input DataFrame is empty")
            return {
                'filtered_data': pd.DataFrame(),
                'max_statistics': {},
                'exercise_found': False,
                'total_records': 0
            }
        
        # Check if required columns exist
        required_columns = ['detailed_exercise_name', 'weight', 'sets', 'reps', 'workout_date']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            error_msg = f"Missing required columns: {missing_columns}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Filter data by exercise name (case-insensitive)
        exercise_name_lower = exercise_name.strip().lower()
        filtered_df = df[df['detailed_exercise_name'].str.lower() == exercise_name_lower].copy()
        
        if filtered_df.empty:
            logger.info(f"No data found for exercise: {exercise_name}")
            return {
                'filtered_data': pd.DataFrame(),
                'max_statistics': {},
                'exercise_found': False,
                'total_records': 0
            }
        
        # Sort by date for time series analysis
        filtered_df = filtered_df.sort_values('workout_date')
        
        # Calculate volume if not already present
        if 'volume' not in filtered_df.columns:
            if all(col in filtered_df.columns for col in ['weight', 'sets', 'reps']):
                filtered_df['volume'] = filtered_df['weight'] * filtered_df['sets'] * filtered_df['reps']
                logger.info("Calculated volume for specific exercise analysis")
        
        # Calculate maximum statistics
        max_statistics = {}
        
        # Max Volume with date
        if 'volume' in filtered_df.columns and not filtered_df['volume'].isna().all():
            max_volume_idx = filtered_df['volume'].idxmax()
            max_statistics['max_volume'] = {
                'value': float(filtered_df.loc[max_volume_idx, 'volume']),
                'date': filtered_df.loc[max_volume_idx, 'workout_date'].strftime('%Y-%m-%d') if isinstance(filtered_df.loc[max_volume_idx, 'workout_date'], pd.Timestamp) else str(filtered_df.loc[max_volume_idx, 'workout_date'])
            }
        
        # Max Weight with date
        if not filtered_df['weight'].isna().all():
            max_weight_idx = filtered_df['weight'].idxmax()
            max_statistics['max_weight'] = {
                'value': float(filtered_df.loc[max_weight_idx, 'weight']),
                'date': filtered_df.loc[max_weight_idx, 'workout_date'].strftime('%Y-%m-%d') if isinstance(filtered_df.loc[max_weight_idx, 'workout_date'], pd.Timestamp) else str(filtered_df.loc[max_weight_idx, 'workout_date'])
            }
        
        # Max Reps with date
        if not filtered_df['reps'].isna().all():
            max_reps_idx = filtered_df['reps'].idxmax()
            max_statistics['max_reps'] = {
                'value': int(filtered_df.loc[max_reps_idx, 'reps']),
                'date': filtered_df.loc[max_reps_idx, 'workout_date'].strftime('%Y-%m-%d') if isinstance(filtered_df.loc[max_reps_idx, 'workout_date'], pd.Timestamp) else str(filtered_df.loc[max_reps_idx, 'workout_date'])
            }
        
        # Max Sets with date
        if not filtered_df['sets'].isna().all():
            max_sets_idx = filtered_df['sets'].idxmax()
            max_statistics['max_sets'] = {
                'value': int(filtered_df.loc[max_sets_idx, 'sets']),
                'date': filtered_df.loc[max_sets_idx, 'workout_date'].strftime('%Y-%m-%d') if isinstance(filtered_df.loc[max_sets_idx, 'workout_date'], pd.Timestamp) else str(filtered_df.loc[max_sets_idx, 'workout_date'])
            }
        
        logger.info(f"Successfully analyzed exercise: {exercise_name} with {len(filtered_df)} records")
        
        return {
            'filtered_data': filtered_df,
            'max_statistics': max_statistics,
            'exercise_found': True,
            'total_records': len(filtered_df)
        }
        
    except Exception as e:
        error_msg = f"Unexpected error during specific exercise analysis: {str(e)}"
        logger.error(error_msg)
        raise


def get_exercise_time_series(exercise_name: str, df: pd.DataFrame) -> pd.DataFrame:
    """
    Get time series data for a specific exercise.
    
    Args:
        exercise_name: Name of the exercise to get time series for
        df: Input DataFrame with workout data
        
    Returns:
        DataFrame with time series data for the specific exercise
    """
    
    try:
        analysis_result = analyze_specific_exercise(exercise_name, df)
        return analysis_result['filtered_data']
        
    except Exception as e:
        logger.error(f"Error getting time series for exercise {exercise_name}: {str(e)}")
        return pd.DataFrame()


def get_exercise_max_statistics(exercise_name: str, df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get maximum statistics for a specific exercise.
    
    Args:
        exercise_name: Name of the exercise to get statistics for
        df: Input DataFrame with workout data
        
    Returns:
        Dictionary with maximum statistics for the exercise
    """
    
    try:
        analysis_result = analyze_specific_exercise(exercise_name, df)
        return analysis_result['max_statistics']
        
    except Exception as e:
        logger.error(f"Error getting max statistics for exercise {exercise_name}: {str(e)}")
        return {} 
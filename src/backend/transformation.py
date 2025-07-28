"""
Data Transformation Module

This module provides data transformation functionality for workout data:
- Field derivation and computation
- Schema modifications
- Data enrichment
"""

import logging
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

# Configure logging
logger = logging.getLogger(__name__)


def derive_fields(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derive additional fields from the workout data.
    
    This function implements BE-007 requirements:
    - Creates 'detailed_exercise_name' by concatenating 'exercise_type' and 'exercise_name'
    - Drops the 'exercise_name' field
    - Creates 'volume' column by multiplying 'weight' * 'sets' * 'reps'
    
    Args:
        df: Input DataFrame with workout data
        
    Returns:
        transformed DataFrame
    """
    
    # Make a copy to avoid modifying original
    df_transformed = df.copy()
    
    try:
        # Step 1: Create 'detailed_exercise_name' column
        if 'exercise_type' in df_transformed.columns and 'exercise_name' in df_transformed.columns:
            df_transformed['detailed_exercise_name'] = (
                df_transformed['exercise_type'] + ' ' + df_transformed['exercise_name']
            )
            logger.info("Created 'detailed_exercise_name' field")
        else:
            error_msg = "Missing required columns 'exercise_type' or 'exercise_name' for detailed_exercise_name creation"
            logger.error(error_msg)
        
        # Step 2: Drop the 'exercise_name' field
        if 'exercise_name' in df_transformed.columns:
            df_transformed = df_transformed.drop(columns=['exercise_name'])
            logger.info("Dropped 'exercise_name' field")
        else:
            error_msg = "Missing required columns 'exercise_name' for detailed_exercise_name creation"
            logger.error(error_msg)
        
        # Step 3: Create 'volume' column
        if all(col in df_transformed.columns for col in ['weight', 'sets', 'reps']):
            df_transformed['volume'] = (
                df_transformed['weight'] * 
                df_transformed['sets'] * 
                df_transformed['reps']
            )
            logger.info("Created 'volume' field")
        else:
            error_msg = "Missing required columns 'weight', 'sets', or 'reps' for volume calculation"
            logger.error(error_msg)
        
        # Validate the final schema
        expected_schema = {
            'workout_date': 'datetime64[ns]',
            'exercise_type': 'object',
            'detailed_exercise_name': 'object',
            'weight': 'float64',
            'sets': 'int64',
            'reps': 'int64',
            'alternating': 'bool',
            'volume': 'float64'
        }
        
        # Check if all expected columns are present
        missing_columns = set(expected_schema.keys()) - set(df_transformed.columns)
        if missing_columns:
            error_msg = f"Missing expected columns after transformation: {missing_columns}"
            logger.error(error_msg)
        
        return df_transformed
        
    except Exception as e:
        error_msg = f"Unexpected error during field derivation: {str(e)}"
        logger.error(error_msg)
        
        return df


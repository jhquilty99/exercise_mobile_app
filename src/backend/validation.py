"""
Simplified Data Validation Module

This module provides essential data validation functionality for workout data:
- Data type coercion
- Basic data constraints validation
- Missing data handling
- Schema standardization
"""

import logging
import pandas as pd
from typing import List, Tuple
from dataclasses import dataclass

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Results of data validation process."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    records_processed: int
    records_valid: int
    records_invalid: int


def clean_workout_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, ValidationResult]:
    """
    Clean and validate workout data, removing invalid records.
    
    Args:
        df: Raw DataFrame to clean and validate
        
    Returns:
        Tuple of (cleaned DataFrame, validation results)
    """
    if df.empty:
        return df, ValidationResult(
            is_valid=True, errors=[], warnings=[], 
            records_processed=0, records_valid=0, records_invalid=0
        )
    
    original_count = len(df)
    errors = []
    warnings = []
    
    # Make a copy to avoid modifying original
    df_clean = df.copy()

    # Step 0: Validate DataFrame structure
    try:
        _validate_sheet_structure(df_clean)
    except ValueError as e:
        errors.append(str(e))
        return df_clean, ValidationResult(
            is_valid=False, errors=errors, warnings=warnings,
            records_processed=original_count, records_valid=0, records_invalid=original_count
        )
    
    # Step 1: Convert data types
    df_clean = _convert_data_types(df_clean, errors, warnings)
    
    # Step 2: Remove rows with missing required fields
    required_fields = ['Workout Date', 'Exercise Name', 'Exercise Type', 'Weight', 'Sets', 'Discrete Reps']
    for field in required_fields:
        if field in df_clean.columns:
            missing_count = df_clean[field].isna().sum()
            if missing_count > 0:
                warnings.append(f"Removing {missing_count} rows with missing {field}")
                df_clean = df_clean.dropna(subset=[field])
    
    # Step 3: Remove rows with negative values
    numeric_fields = ['Weight', 'Sets', 'Discrete Reps']
    for field in numeric_fields:
        if field in df_clean.columns:
            negative_count = (df_clean[field] < 0).sum()
            if negative_count > 0:
                errors.append(f"Removing {negative_count} rows with negative {field}")
                df_clean = df_clean[df_clean[field] >= 0]
    
    # Step 4: Remove duplicate records
    duplicate_count = df_clean.duplicated().sum()
    if duplicate_count > 0:
        warnings.append(f"Removing {duplicate_count} duplicate records")
        df_clean = df_clean.drop_duplicates()
    
    # Step 5: Standardize schema
    df_clean = _standardize_schema(df_clean)
    
    # Calculate final statistics
    final_count = len(df_clean)
    records_invalid = original_count - final_count
    
    validation_result = ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        records_processed=original_count,
        records_valid=final_count,
        records_invalid=records_invalid
    )
    
    logger.info(f"Data cleaning completed. {final_count}/{original_count} records valid")
    
    return df_clean, validation_result


def _convert_data_types(df: pd.DataFrame, errors: List[str], warnings: List[str]) -> pd.DataFrame:
    """Convert data to proper types with error handling."""
    try:
        # Convert date column
        if 'Workout Date' in df.columns:
            df['Workout Date'] = pd.to_datetime(df['Workout Date'], errors='coerce')
            invalid_dates = df['Workout Date'].isna().sum()
            if invalid_dates > 0:
                warnings.append(f"Found {invalid_dates} invalid dates")
        
        # Convert numeric columns
        numeric_columns = ['Weight', 'Sets', 'Discrete Reps']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                invalid_nums = df[col].isna().sum()
                if invalid_nums > 0:
                    warnings.append(f"Found {invalid_nums} invalid numeric values in {col}")
        
        # Convert boolean column
        if 'Alternating' in df.columns:
            df['Alternating'] = df['Alternating'].astype(str).str.lower().map({
                'true': True, 'false': False, 'yes': True, 'no': False
            }).fillna(False)
        
        # Ensure string columns
        string_columns = ['Exercise Name', 'Exercise Type']
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].astype(str)
        
    except Exception as e:
        errors.append(f"Error converting data types: {str(e)}")
    
    return df


def _standardize_schema(df: pd.DataFrame) -> pd.DataFrame:
    """Convert DataFrame to standardized schema."""
    column_mapping = {
        'Workout Date': 'workout_date',
        'Exercise Type': 'exercise_type',
        'Exercise Name': 'exercise_name',
        'Weight': 'weight',
        'Sets': 'sets',
        'Discrete Reps': 'reps',
        'Alternating': 'alternating'
    }
    
    # Rename columns
    df = df.rename(columns=column_mapping)
    
    # Ensure proper data types for final schema
    if 'workout_date' in df.columns:
        df['workout_date'] = pd.to_datetime(df['workout_date'])
    if 'weight' in df.columns:
        df['weight'] = df['weight'].astype('float64')
    if 'sets' in df.columns:
        df['sets'] = df['sets'].astype('Int64')
    if 'reps' in df.columns:
        df['reps'] = df['reps'].astype('Int64')
    if 'alternating' in df.columns:
        df['alternating'] = df['alternating'].astype(bool)
    
    return df

def _validate_sheet_structure(df: pd.DataFrame) -> None:
    """Validate DataFrame structure."""
    try:
        required_columns = [
            'Workout Date', 'Exercise Type', 'Exercise Name', 
            'Weight', 'Sets', 'Discrete Reps', 'Alternating'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
    except Exception as e:
        logger.error(f"Error validating DataFrame structure: {e}")
        raise

"""
Data Validation and Transformation Module

This module provides comprehensive validation and transformation functions for workout data
to ensure data quality and adherence to the specified schema requirements.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, date
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
    validation_summary: Dict[str, Any]


class WorkoutDataValidator:
    """
    Comprehensive validator for workout data ensuring adherence to schema and business rules.
    
    Validates:
    - Required fields presence
    - Data types compliance
    - Data constraints (non-negative values, valid dates)
    - Exercise name standardization
    - Missing/duplicate value handling
    """
    
    def __init__(self):
        """Initialize the validator with target schema and validation rules."""
        self.target_schema = {
            'workout_date': 'datetime64[ns]',
            'exercise_type': 'string',
            'exercise_name': 'string', 
            'weight_lbs': 'int64',
            'sets': 'int64',
            'discrete_reps': 'int64',
            'alternating': 'boolean'
        }
        
        self.column_mapping = {
            'Workout Date': 'workout_date',
            'Exercise Type': 'exercise_type',
            'Exercise Name': 'exercise_name',
            'Weight': 'weight_lbs',
            'Sets': 'sets',
            'Discrete Reps': 'discrete_reps',
            'Alternating': 'alternating'
        }
        
        self.validation_rules = {
            'weight_lbs': lambda x: x >= 0,
            'sets': lambda x: x >= 0,
            'discrete_reps': lambda x: x >= 0,
            'workout_date': lambda x: pd.notna(x) and isinstance(x, (datetime, date, pd.Timestamp)),
            'exercise_name': lambda x: isinstance(x, str) and len(x.strip()) > 0,
            'exercise_type': lambda x: isinstance(x, str) and len(x.strip()) > 0
        }
    
    def validate_dataframe(self, df: pd.DataFrame) -> ValidationResult:
        """
        Comprehensive validation of workout DataFrame against schema requirements.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            ValidationResult with detailed validation information
        """
        errors = []
        warnings = []
        records_processed = len(df)
        records_valid = 0
        records_invalid = 0
        
        logger.info(f"Starting validation of DataFrame with {records_processed} records")
        
        # Step 1: Validate required fields
        required_fields_result = self._validate_required_fields(df)
        errors.extend(required_fields_result['errors'])
        warnings.extend(required_fields_result['warnings'])
        
        # Step 2: Enforce proper data types
        data_types_result = self._validate_data_types(df)
        errors.extend(data_types_result['errors'])
        warnings.extend(data_types_result['warnings'])
        
        # Step 3: Enforce data constraints
        constraints_result = self._validate_data_constraints(df)
        errors.extend(constraints_result['errors'])
        warnings.extend(constraints_result['warnings'])
        
        # Step 4: Identify and handle missing/duplicate values
        missing_duplicate_result = self._validate_missing_duplicate_values(df)
        errors.extend(missing_duplicate_result['errors'])
        warnings.extend(missing_duplicate_result['warnings'])
        
        # Step 5: Validate exercise names
        exercise_names_result = self._validate_exercise_names(df)
        errors.extend(exercise_names_result['errors'])
        warnings.extend(exercise_names_result['warnings'])
        
        # Step 6: Convert to standardized schema
        schema_result = self._convert_to_standardized_schema(df)
        errors.extend(schema_result['errors'])
        warnings.extend(schema_result['warnings'])
        
        # Calculate validation statistics
        if not errors:
            records_valid = records_processed
            records_invalid = 0
        else:
            # Estimate invalid records based on error types
            records_invalid = len([e for e in errors if 'Row' in e])
            records_valid = records_processed - records_invalid
        
        validation_summary = {
            'schema_compliance': len(data_types_result['errors']) == 0,
            'constraint_compliance': len(constraints_result['errors']) == 0,
            'data_quality_score': (records_valid / records_processed) if records_processed > 0 else 0,
            'missing_data_percentage': missing_duplicate_result.get('missing_percentage', 0),
            'duplicate_records': missing_duplicate_result.get('duplicate_count', 0)
        }
        
        is_valid = len(errors) == 0
        
        logger.info(f"Validation completed. Valid: {records_valid}, Invalid: {records_invalid}")
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            records_processed=records_processed,
            records_valid=records_valid,
            records_invalid=records_invalid,
            validation_summary=validation_summary
        )
    
    def _validate_required_fields(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Validate that all required fields are present in the DataFrame."""
        errors = []
        warnings = []
        
        required_columns = ['Workout Date', 'Exercise Name', 'Exercise Type', 'Weight', 'Sets', 'Discrete Reps']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            errors.append(f"Missing required columns: {missing_columns}")
        
        # Check for completely empty required columns
        for col in required_columns:
            if col in df.columns and df[col].isna().all():
                errors.append(f"Required column '{col}' contains only missing values")
        
        return {'errors': errors, 'warnings': warnings}
    
    def _validate_data_types(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Validate and enforce proper data types according to target schema."""
        errors = []
        warnings = []
        
        for col, target_type in self.column_mapping.items():
            if col not in df.columns:
                continue
                
            try:
                if target_type == 'workout_date':
                    # Convert to datetime
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    invalid_dates = df[col].isna().sum()
                    if invalid_dates > 0:
                        warnings.append(f"Column '{col}': {invalid_dates} invalid date values found")
                
                elif target_type in ['weight_lbs', 'sets', 'discrete_reps']:
                    # Convert to numeric
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    invalid_nums = df[col].isna().sum()
                    if invalid_nums > 0:
                        warnings.append(f"Column '{col}': {invalid_nums} invalid numeric values found")
                
                elif target_type == 'alternating':
                    # Convert to boolean
                    df[col] = df[col].astype(str).str.lower().map({'true': True, 'false': False, 'yes': True, 'no': False})
                    # Fill NaN with False as default
                    df[col] = df[col].fillna(False)
                
                elif target_type in ['exercise_name', 'exercise_type']:
                    # Ensure string type
                    df[col] = df[col].astype(str)
                    
            except Exception as e:
                errors.append(f"Error converting column '{col}' to {target_type}: {str(e)}")
        
        return {'errors': errors, 'warnings': warnings}
    
    def _validate_data_constraints(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Enforce data constraints (non-negative weights, sets, reps)."""
        errors = []
        warnings = []
        
        # Validate weight constraints
        if 'Weight' in df.columns:
            negative_weights = (df['Weight'] < 0).sum()
            if negative_weights > 0:
                errors.append(f"Found {negative_weights} records with negative weights")
            
            zero_weights = (df['Weight'] == 0).sum()
            if zero_weights > 0:
                warnings.append(f"Found {zero_weights} records with zero weights")
        
        # Validate sets constraints
        if 'Sets' in df.columns:
            negative_sets = (df['Sets'] < 0).sum()
            if negative_sets > 0:
                errors.append(f"Found {negative_sets} records with negative sets")
            
            zero_sets = (df['Sets'] == 0).sum()
            if zero_sets > 0:
                warnings.append(f"Found {zero_sets} records with zero sets")
        
        # Validate reps constraints
        if 'Discrete Reps' in df.columns:
            negative_reps = (df['Discrete Reps'] < 0).sum()
            if negative_reps > 0:
                errors.append(f"Found {negative_reps} records with negative reps")
            
            zero_reps = (df['Discrete Reps'] == 0).sum()
            if zero_reps > 0:
                warnings.append(f"Found {zero_reps} records with zero reps")
        
        # Validate date constraints
        if 'Workout Date' in df.columns:
            future_dates = (df['Workout Date'] > pd.Timestamp.now()).sum()
            if future_dates > 0:
                warnings.append(f"Found {future_dates} records with future dates")
        
        return {'errors': errors, 'warnings': warnings}
    
    def _validate_missing_duplicate_values(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Identify and handle missing/duplicate values."""
        errors = []
        warnings = []
        
        # Check for missing values in required fields
        required_fields = ['Workout Date', 'Exercise Name', 'Exercise Type', 'Weight', 'Sets', 'Discrete Reps']
        missing_counts = {}
        
        for field in required_fields:
            if field in df.columns:
                missing_count = df[field].isna().sum()
                if missing_count > 0:
                    missing_counts[field] = missing_count
                    warnings.append(f"Column '{field}': {missing_count} missing values")
        
        # Calculate missing data percentage
        total_cells = len(df) * len(required_fields)
        missing_cells = sum(missing_counts.values())
        missing_percentage = (missing_cells / total_cells) * 100 if total_cells > 0 else 0
        
        if missing_percentage > 10:
            warnings.append(f"High missing data percentage: {missing_percentage:.1f}%")
        
        # Check for duplicate records
        if len(df.columns) > 0:
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                warnings.append(f"Found {duplicates} duplicate records")
        
        return {
            'errors': errors, 
            'warnings': warnings,
            'missing_percentage': missing_percentage,
            'duplicate_count': duplicates if 'duplicates' in locals() else 0
        }
    
    def _validate_exercise_names(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Validate exercise names (case-insensitive, standardized)."""
        errors = []
        warnings = []
        
        if 'Exercise Name' not in df.columns:
            return {'errors': errors, 'warnings': warnings}
        
        # Check for empty exercise names
        empty_names = (df['Exercise Name'].str.strip() == '').sum()
        if empty_names > 0:
            errors.append(f"Found {empty_names} records with empty exercise names")
        
        # Check for very short exercise names (likely typos)
        short_names = (df['Exercise Name'].str.len() < 3).sum()
        if short_names > 0:
            warnings.append(f"Found {short_names} records with very short exercise names (< 3 characters)")
        
        # Standardize exercise names (trim whitespace, title case)
        df['Exercise Name'] = df['Exercise Name'].str.strip().str.title()
        
        # Check for common variations and suggest standardization
        unique_names = df['Exercise Name'].unique()
        if len(unique_names) > 50:
            warnings.append(f"Large number of unique exercise names ({len(unique_names)}), consider standardization")
        
        return {'errors': errors, 'warnings': warnings}
    
    def _convert_to_standardized_schema(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Convert DataFrame to standardized WorkoutLog schema."""
        errors = []
        warnings = []
        
        try:
            # Rename columns to match target schema
            df_standardized = df.rename(columns=self.column_mapping)
            
            # Ensure all required columns exist
            missing_schema_cols = [col for col in self.target_schema.keys() if col not in df_standardized.columns]
            if missing_schema_cols:
                errors.append(f"Missing columns in standardized schema: {missing_schema_cols}")
            
            # Convert data types to match target schema
            for col, target_type in self.target_schema.items():
                if col in df_standardized.columns:
                    try:
                        if target_type == 'datetime64[ns]':
                            df_standardized[col] = pd.to_datetime(df_standardized[col])
                        elif target_type == 'int64':
                            df_standardized[col] = pd.to_numeric(df_standardized[col], errors='coerce').astype('Int64')
                        elif target_type == 'boolean':
                            df_standardized[col] = df_standardized[col].astype(bool)
                        elif target_type == 'string':
                            df_standardized[col] = df_standardized[col].astype(str)
                    except Exception as e:
                        errors.append(f"Error converting column '{col}' to {target_type}: {str(e)}")
            
            # Update the original DataFrame
            df.clear()
            df.update(df_standardized)
            
            logger.info("Successfully converted DataFrame to standardized schema")
            
        except Exception as e:
            errors.append(f"Error converting to standardized schema: {str(e)}")
        
        return {'errors': errors, 'warnings': warnings}
    
    def clean_and_validate_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, ValidationResult]:
        """
        Clean and validate workout data, removing invalid records.
        
        Args:
            df: Raw DataFrame to clean and validate
            
        Returns:
            Tuple of (cleaned DataFrame, validation results)
        """
        # Make a copy to avoid modifying original
        df_clean = df.copy()
        
        # Perform validation
        validation_result = self.validate_dataframe(df_clean)
        
        # Remove invalid records based on critical errors
        if not validation_result.is_valid:
            # Remove rows with missing required fields
            required_fields = ['Workout Date', 'Exercise Name', 'Exercise Type', 'Weight', 'Sets', 'Discrete Reps']
            for field in required_fields:
                if field in df_clean.columns:
                    df_clean = df_clean.dropna(subset=[field])
            
            # Remove rows with negative values
            numeric_fields = ['Weight', 'Sets', 'Discrete Reps']
            for field in numeric_fields:
                if field in df_clean.columns:
                    df_clean = df_clean[df_clean[field] >= 0]
            
            # Remove rows with invalid dates
            if 'Workout Date' in df_clean.columns:
                df_clean = df_clean.dropna(subset=['Workout Date'])
        
        # Remove duplicate records
        df_clean = df_clean.drop_duplicates()
        
        # Update validation result with final counts
        final_count = len(df_clean)
        validation_result.records_valid = final_count
        validation_result.records_invalid = validation_result.records_processed - final_count
        
        logger.info(f"Data cleaning completed. Final record count: {final_count}")
        
        return df_clean, validation_result


def validate_workout_data(df: pd.DataFrame) -> ValidationResult:
    """
    Convenience function to validate workout data.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        ValidationResult with validation details
    """
    validator = WorkoutDataValidator()
    return validator.validate_dataframe(df)


def clean_workout_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, ValidationResult]:
    """
    Convenience function to clean and validate workout data.
    
    Args:
        df: Raw DataFrame to clean and validate
        
    Returns:
        Tuple of (cleaned DataFrame, validation results)
    """
    validator = WorkoutDataValidator()
    return validator.clean_and_validate_data(df)

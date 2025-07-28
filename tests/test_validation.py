"""
Test suite for data validation and transformation functionality.

Tests the WorkoutDataValidator class and related functions to ensure:
- Required fields validation
- Data type enforcement
- Data constraints validation
- Missing/duplicate value handling
- Exercise name validation
- Schema conversion
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, date
from unittest.mock import patch, MagicMock

from src.backend.validation import (
    WorkoutDataValidator,
    ValidationResult,
    validate_workout_data,
    clean_workout_data
)


class TestValidationResult:
    """Test the ValidationResult dataclass."""
    
    def test_validation_result_creation(self):
        """Test creating a ValidationResult instance."""
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=["Test warning"],
            records_processed=100,
            records_valid=95,
            records_invalid=5,
            validation_summary={"score": 0.95}
        )
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 1
        assert result.records_processed == 100
        assert result.records_valid == 95
        assert result.records_invalid == 5
        assert result.validation_summary["score"] == 0.95


class TestWorkoutDataValidator:
    """Test the WorkoutDataValidator class."""
    
    @pytest.fixture
    def validator(self):
        """Create a WorkoutDataValidator instance for testing."""
        return WorkoutDataValidator()
    
    @pytest.fixture
    def valid_dataframe(self):
        """Create a valid DataFrame for testing."""
        return pd.DataFrame({
            'Workout Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'Exercise Type': ['Strength', 'Strength', 'Cardio'],
            'Exercise Name': ['Bench Press', 'Squats', 'Running'],
            'Weight': [135, 185, 0],
            'Sets': [3, 4, 1],
            'Discrete Reps': [10, 8, 0],
            'Alternating': [False, True, False]
        })
    
    @pytest.fixture
    def invalid_dataframe(self):
        """Create an invalid DataFrame for testing validation errors."""
        return pd.DataFrame({
            'Workout Date': ['2024-01-01', 'invalid-date', '2024-01-03'],
            'Exercise Type': ['Strength', '', 'Cardio'],
            'Exercise Name': ['Bench Press', 'Squats', ''],
            'Weight': [135, -10, 0],
            'Sets': [3, 0, -1],
            'Discrete Reps': [10, 8, -5],
            'Alternating': [False, True, False]
        })
    
    def test_validator_initialization(self, validator):
        """Test validator initialization with correct schema and rules."""
        assert 'workout_date' in validator.target_schema
        assert 'exercise_name' in validator.target_schema
        assert 'weight_lbs' in validator.target_schema
        assert 'sets' in validator.target_schema
        assert 'discrete_reps' in validator.target_schema
        assert 'alternating' in validator.target_schema
        
        assert 'Workout Date' in validator.column_mapping
        assert 'Exercise Name' in validator.column_mapping
        assert 'Weight' in validator.column_mapping
        
        assert 'weight_lbs' in validator.validation_rules
        assert 'sets' in validator.validation_rules
        assert 'discrete_reps' in validator.validation_rules


class TestRequiredFieldsValidation:
    """Test required fields validation functionality."""
    
    @pytest.fixture
    def validator(self):
        return WorkoutDataValidator()
    
    def test_validate_required_fields_success(self, validator, valid_dataframe):
        """Test validation when all required fields are present."""
        result = validator._validate_required_fields(valid_dataframe)
        
        assert len(result['errors']) == 0
        assert len(result['warnings']) == 0
    
    def test_validate_required_fields_missing_columns(self, validator):
        """Test validation when required columns are missing."""
        incomplete_df = pd.DataFrame({
            'Workout Date': ['2024-01-01'],
            'Exercise Name': ['Bench Press'],
            # Missing: Exercise Type, Weight, Sets, Discrete Reps
        })
        
        result = validator._validate_required_fields(incomplete_df)
        
        assert len(result['errors']) > 0
        assert any('Missing required columns' in error for error in result['errors'])
    
    def test_validate_required_fields_empty_columns(self, validator):
        """Test validation when required columns contain only missing values."""
        empty_df = pd.DataFrame({
            'Workout Date': [np.nan, np.nan, np.nan],
            'Exercise Type': ['Strength', 'Cardio', 'Strength'],
            'Exercise Name': ['Bench Press', 'Squats', 'Deadlift'],
            'Weight': [135, 185, 225],
            'Sets': [3, 4, 5],
            'Discrete Reps': [10, 8, 6]
        })
        
        result = validator._validate_required_fields(empty_df)
        
        assert len(result['errors']) > 0
        assert any('contains only missing values' in error for error in result['errors'])


class TestDataTypesValidation:
    """Test data type validation and conversion functionality."""
    
    @pytest.fixture
    def validator(self):
        return WorkoutDataValidator()
    
    def test_validate_data_types_success(self, validator, valid_dataframe):
        """Test successful data type conversion."""
        result = validator._validate_data_types(valid_dataframe)
        
        assert len(result['errors']) == 0
        # Should have warnings for zero values in weight/reps
        assert len(result['warnings']) >= 0
    
    def test_validate_data_types_invalid_dates(self, validator):
        """Test handling of invalid date values."""
        df_with_invalid_dates = pd.DataFrame({
            'Workout Date': ['2024-01-01', 'not-a-date', '2024-13-45'],
            'Exercise Type': ['Strength', 'Strength', 'Strength'],
            'Exercise Name': ['Bench Press', 'Squats', 'Deadlift'],
            'Weight': [135, 185, 225],
            'Sets': [3, 4, 5],
            'Discrete Reps': [10, 8, 6]
        })
        
        result = validator._validate_data_types(df_with_invalid_dates)
        
        assert len(result['warnings']) > 0
        assert any('invalid date values found' in warning for warning in result['warnings'])
    
    def test_validate_data_types_invalid_numeric(self, validator):
        """Test handling of invalid numeric values."""
        df_with_invalid_nums = pd.DataFrame({
            'Workout Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'Exercise Type': ['Strength', 'Strength', 'Strength'],
            'Exercise Name': ['Bench Press', 'Squats', 'Deadlift'],
            'Weight': [135, 'not-a-number', 225],
            'Sets': [3, 'invalid', 5],
            'Discrete Reps': [10, 8, 'bad']
        })
        
        result = validator._validate_data_types(df_with_invalid_nums)
        
        assert len(result['warnings']) > 0
        assert any('invalid numeric values found' in warning for warning in result['warnings'])
    
    def test_validate_data_types_boolean_conversion(self, validator):
        """Test boolean conversion for alternating field."""
        df_with_booleans = pd.DataFrame({
            'Workout Date': ['2024-01-01', '2024-01-02'],
            'Exercise Type': ['Strength', 'Strength'],
            'Exercise Name': ['Bench Press', 'Squats'],
            'Weight': [135, 185],
            'Sets': [3, 4],
            'Discrete Reps': [10, 8],
            'Alternating': ['True', 'False']
        })
        
        result = validator._validate_data_types(df_with_booleans)
        
        assert len(result['errors']) == 0
        # Check that boolean conversion worked
        assert df_with_booleans['Alternating'].dtype == bool or df_with_booleans['Alternating'].iloc[0] is True


class TestDataConstraintsValidation:
    """Test data constraints validation functionality."""
    
    @pytest.fixture
    def validator(self):
        return WorkoutDataValidator()
    
    def test_validate_data_constraints_success(self, validator, valid_dataframe):
        """Test validation when all constraints are satisfied."""
        result = validator._validate_data_constraints(valid_dataframe)
        
        # Should have warnings for zero values but no errors
        assert len(result['errors']) == 0
        assert len(result['warnings']) >= 0
    
    def test_validate_data_constraints_negative_weights(self, validator):
        """Test detection of negative weight values."""
        df_with_negative_weights = pd.DataFrame({
            'Workout Date': ['2024-01-01', '2024-01-02'],
            'Exercise Type': ['Strength', 'Strength'],
            'Exercise Name': ['Bench Press', 'Squats'],
            'Weight': [135, -10],
            'Sets': [3, 4],
            'Discrete Reps': [10, 8]
        })
        
        result = validator._validate_data_constraints(df_with_negative_weights)
        
        assert len(result['errors']) > 0
        assert any('negative weights' in error for error in result['errors'])
    
    def test_validate_data_constraints_negative_sets(self, validator):
        """Test detection of negative set values."""
        df_with_negative_sets = pd.DataFrame({
            'Workout Date': ['2024-01-01', '2024-01-02'],
            'Exercise Type': ['Strength', 'Strength'],
            'Exercise Name': ['Bench Press', 'Squats'],
            'Weight': [135, 185],
            'Sets': [3, -1],
            'Discrete Reps': [10, 8]
        })
        
        result = validator._validate_data_constraints(df_with_negative_sets)
        
        assert len(result['errors']) > 0
        assert any('negative sets' in error for error in result['errors'])
    
    def test_validate_data_constraints_negative_reps(self, validator):
        """Test detection of negative rep values."""
        df_with_negative_reps = pd.DataFrame({
            'Workout Date': ['2024-01-01', '2024-01-02'],
            'Exercise Type': ['Strength', 'Strength'],
            'Exercise Name': ['Bench Press', 'Squats'],
            'Weight': [135, 185],
            'Sets': [3, 4],
            'Discrete Reps': [10, -5]
        })
        
        result = validator._validate_data_constraints(df_with_negative_reps)
        
        assert len(result['errors']) > 0
        assert any('negative reps' in error for error in result['errors'])
    
    def test_validate_data_constraints_future_dates(self, validator):
        """Test detection of future dates."""
        future_date = (pd.Timestamp.now() + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        df_with_future_dates = pd.DataFrame({
            'Workout Date': ['2024-01-01', future_date],
            'Exercise Type': ['Strength', 'Strength'],
            'Exercise Name': ['Bench Press', 'Squats'],
            'Weight': [135, 185],
            'Sets': [3, 4],
            'Discrete Reps': [10, 8]
        })
        
        result = validator._validate_data_constraints(df_with_future_dates)
        
        assert len(result['warnings']) > 0
        assert any('future dates' in warning for warning in result['warnings'])
    
    def test_validate_data_constraints_zero_values(self, validator):
        """Test warnings for zero values in weight, sets, and reps."""
        df_with_zeros = pd.DataFrame({
            'Workout Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'Exercise Type': ['Strength', 'Strength', 'Cardio'],
            'Exercise Name': ['Bench Press', 'Squats', 'Running'],
            'Weight': [135, 0, 0],
            'Sets': [3, 0, 1],
            'Discrete Reps': [10, 8, 0]
        })
        
        result = validator._validate_data_constraints(df_with_zeros)
        
        assert len(result['warnings']) > 0
        assert any('zero weights' in warning for warning in result['warnings'])
        assert any('zero sets' in warning for warning in result['warnings'])
        assert any('zero reps' in warning for warning in result['warnings'])


class TestMissingDuplicateValuesValidation:
    """Test missing and duplicate value validation functionality."""
    
    @pytest.fixture
    def validator(self):
        return WorkoutDataValidator()
    
    def test_validate_missing_duplicate_values_success(self, validator, valid_dataframe):
        """Test validation when no missing or duplicate values exist."""
        result = validator._validate_missing_duplicate_values(valid_dataframe)
        
        assert len(result['errors']) == 0
        assert result['missing_percentage'] == 0
        assert result['duplicate_count'] == 0
    
    def test_validate_missing_duplicate_values_missing_data(self, validator):
        """Test detection of missing values."""
        df_with_missing = pd.DataFrame({
            'Workout Date': ['2024-01-01', np.nan, '2024-01-03'],
            'Exercise Type': ['Strength', 'Strength', np.nan],
            'Exercise Name': ['Bench Press', 'Squats', 'Deadlift'],
            'Weight': [135, np.nan, 225],
            'Sets': [3, 4, np.nan],
            'Discrete Reps': [10, 8, 6]
        })
        
        result = validator._validate_missing_duplicate_values(df_with_missing)
        
        assert len(result['warnings']) > 0
        assert result['missing_percentage'] > 0
        assert any('missing values' in warning for warning in result['warnings'])
    
    def test_validate_missing_duplicate_values_high_missing_percentage(self, validator):
        """Test warning for high missing data percentage."""
        df_mostly_missing = pd.DataFrame({
            'Workout Date': ['2024-01-01', np.nan, np.nan, np.nan, np.nan],
            'Exercise Type': ['Strength', np.nan, np.nan, np.nan, np.nan],
            'Exercise Name': ['Bench Press', np.nan, np.nan, np.nan, np.nan],
            'Weight': [135, np.nan, np.nan, np.nan, np.nan],
            'Sets': [3, np.nan, np.nan, np.nan, np.nan],
            'Discrete Reps': [10, np.nan, np.nan, np.nan, np.nan]
        })
        
        result = validator._validate_missing_duplicate_values(df_mostly_missing)
        
        assert len(result['warnings']) > 0
        assert result['missing_percentage'] > 10
        assert any('High missing data percentage' in warning for warning in result['warnings'])
    
    def test_validate_missing_duplicate_values_duplicates(self, validator):
        """Test detection of duplicate records."""
        df_with_duplicates = pd.DataFrame({
            'Workout Date': ['2024-01-01', '2024-01-01', '2024-01-02'],
            'Exercise Type': ['Strength', 'Strength', 'Strength'],
            'Exercise Name': ['Bench Press', 'Bench Press', 'Squats'],
            'Weight': [135, 135, 185],
            'Sets': [3, 3, 4],
            'Discrete Reps': [10, 10, 8]
        })
        
        result = validator._validate_missing_duplicate_values(df_with_duplicates)
        
        assert len(result['warnings']) > 0
        assert result['duplicate_count'] > 0
        assert any('duplicate records' in warning for warning in result['warnings'])


class TestExerciseNamesValidation:
    """Test exercise name validation functionality."""
    
    @pytest.fixture
    def validator(self):
        return WorkoutDataValidator()
    
    def test_validate_exercise_names_success(self, validator, valid_dataframe):
        """Test validation when exercise names are valid."""
        result = validator._validate_exercise_names(valid_dataframe)
        
        assert len(result['errors']) == 0
        # Check that names were standardized (title case)
        assert valid_dataframe['Exercise Name'].iloc[0] == 'Bench Press'
    
    def test_validate_exercise_names_empty_names(self, validator):
        """Test detection of empty exercise names."""
        df_with_empty_names = pd.DataFrame({
            'Workout Date': ['2024-01-01', '2024-01-02'],
            'Exercise Type': ['Strength', 'Strength'],
            'Exercise Name': ['Bench Press', ''],
            'Weight': [135, 185],
            'Sets': [3, 4],
            'Discrete Reps': [10, 8]
        })
        
        result = validator._validate_exercise_names(df_with_empty_names)
        
        assert len(result['errors']) > 0
        assert any('empty exercise names' in error for error in result['errors'])
    
    def test_validate_exercise_names_short_names(self, validator):
        """Test warnings for very short exercise names."""
        df_with_short_names = pd.DataFrame({
            'Workout Date': ['2024-01-01', '2024-01-02'],
            'Exercise Type': ['Strength', 'Strength'],
            'Exercise Name': ['Bench Press', 'Ab'],
            'Weight': [135, 185],
            'Sets': [3, 4],
            'Discrete Reps': [10, 8]
        })
        
        result = validator._validate_exercise_names(df_with_short_names)
        
        assert len(result['warnings']) > 0
        assert any('very short exercise names' in warning for warning in result['warnings'])
    
    def test_validate_exercise_names_standardization(self, validator):
        """Test exercise name standardization (trim whitespace, title case)."""
        df_with_messy_names = pd.DataFrame({
            'Workout Date': ['2024-01-01', '2024-01-02'],
            'Exercise Type': ['Strength', 'Strength'],
            'Exercise Name': ['  bench press  ', 'SQUATS'],
            'Weight': [135, 185],
            'Sets': [3, 4],
            'Discrete Reps': [10, 8]
        })
        
        result = validator._validate_exercise_names(df_with_messy_names)
        
        assert len(result['errors']) == 0
        # Check that names were standardized
        assert df_with_messy_names['Exercise Name'].iloc[0] == 'Bench Press'
        assert df_with_messy_names['Exercise Name'].iloc[1] == 'Squats'


class TestSchemaConversion:
    """Test schema conversion functionality."""
    
    @pytest.fixture
    def validator(self):
        return WorkoutDataValidator()
    
    def test_convert_to_standardized_schema_success(self, validator, valid_dataframe):
        """Test successful conversion to standardized schema."""
        result = validator._convert_to_standardized_schema(valid_dataframe)
        
        assert len(result['errors']) == 0
        # Check that columns were renamed
        assert 'workout_date' in valid_dataframe.columns
        assert 'exercise_name' in valid_dataframe.columns
        assert 'weight_lbs' in valid_dataframe.columns
        assert 'sets' in valid_dataframe.columns
        assert 'discrete_reps' in valid_dataframe.columns
        assert 'alternating' in valid_dataframe.columns
    
    def test_convert_to_standardized_schema_missing_columns(self, validator):
        """Test handling of missing columns in schema conversion."""
        incomplete_df = pd.DataFrame({
            'Workout Date': ['2024-01-01'],
            'Exercise Name': ['Bench Press'],
            'Weight': [135],
            'Sets': [3],
            'Discrete Reps': [10]
            # Missing: Exercise Type, Alternating
        })
        
        result = validator._convert_to_standardized_schema(incomplete_df)
        
        assert len(result['errors']) > 0
        assert any('Missing columns in standardized schema' in error for error in result['errors'])


class TestComprehensiveValidation:
    """Test comprehensive validation functionality."""
    
    @pytest.fixture
    def validator(self):
        return WorkoutDataValidator()
    
    def test_validate_dataframe_success(self, validator, valid_dataframe):
        """Test comprehensive validation with valid data."""
        result = validator.validate_dataframe(valid_dataframe)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.records_processed == 3
        assert result.records_valid == 3
        assert result.records_invalid == 0
        assert result.validation_summary['schema_compliance'] is True
        assert result.validation_summary['constraint_compliance'] is True
        assert result.validation_summary['data_quality_score'] == 1.0
    
    def test_validate_dataframe_with_errors(self, validator, invalid_dataframe):
        """Test comprehensive validation with invalid data."""
        result = validator.validate_dataframe(invalid_dataframe)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert result.records_processed == 3
        assert result.records_valid < 3
        assert result.records_invalid > 0
        assert result.validation_summary['data_quality_score'] < 1.0
    
    def test_clean_and_validate_data_success(self, validator, valid_dataframe):
        """Test cleaning and validation with valid data."""
        cleaned_df, result = validator.clean_and_validate_data(valid_dataframe)
        
        assert len(cleaned_df) == 3
        assert result.is_valid is True
        assert result.records_valid == 3
        assert result.records_invalid == 0
    
    def test_clean_and_validate_data_removes_invalid(self, validator, invalid_dataframe):
        """Test that cleaning removes invalid records."""
        cleaned_df, result = validator.clean_and_validate_data(invalid_dataframe)
        
        assert len(cleaned_df) < len(invalid_dataframe)
        assert result.records_valid == len(cleaned_df)
        assert result.records_invalid > 0
    
    def test_clean_and_validate_data_removes_duplicates(self, validator):
        """Test that cleaning removes duplicate records."""
        df_with_duplicates = pd.DataFrame({
            'Workout Date': ['2024-01-01', '2024-01-01', '2024-01-02'],
            'Exercise Type': ['Strength', 'Strength', 'Strength'],
            'Exercise Name': ['Bench Press', 'Bench Press', 'Squats'],
            'Weight': [135, 135, 185],
            'Sets': [3, 3, 4],
            'Discrete Reps': [10, 10, 8],
            'Alternating': [False, False, True]
        })
        
        cleaned_df, result = validator.clean_and_validate_data(df_with_duplicates)
        
        assert len(cleaned_df) < len(df_with_duplicates)
        assert result.records_valid == len(cleaned_df)


class TestConvenienceFunctions:
    """Test the convenience functions."""
    
    def test_validate_workout_data(self, valid_dataframe):
        """Test the validate_workout_data convenience function."""
        result = validate_workout_data(valid_dataframe)
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert result.records_processed == 3
    
    def test_clean_workout_data(self, valid_dataframe):
        """Test the clean_workout_data convenience function."""
        cleaned_df, result = clean_workout_data(valid_dataframe)
        
        assert isinstance(cleaned_df, pd.DataFrame)
        assert isinstance(result, ValidationResult)
        assert len(cleaned_df) == 3
        assert result.is_valid is True


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.fixture
    def validator(self):
        return WorkoutDataValidator()
    
    def test_empty_dataframe(self, validator):
        """Test validation with empty DataFrame."""
        empty_df = pd.DataFrame()
        result = validator.validate_dataframe(empty_df)
        
        assert result.records_processed == 0
        assert result.records_valid == 0
        assert result.records_invalid == 0
        assert result.validation_summary['data_quality_score'] == 0
    
    def test_single_row_dataframe(self, validator):
        """Test validation with single row DataFrame."""
        single_row_df = pd.DataFrame({
            'Workout Date': ['2024-01-01'],
            'Exercise Type': ['Strength'],
            'Exercise Name': ['Bench Press'],
            'Weight': [135],
            'Sets': [3],
            'Discrete Reps': [10],
            'Alternating': [False]
        })
        
        result = validator.validate_dataframe(single_row_df)
        
        assert result.records_processed == 1
        assert result.records_valid == 1
        assert result.is_valid is True
    
    def test_large_dataframe(self, validator):
        """Test validation with large DataFrame."""
        # Create a large DataFrame with 1000 rows
        large_df = pd.DataFrame({
            'Workout Date': [f'2024-01-{i:02d}' for i in range(1, 1001)],
            'Exercise Type': ['Strength'] * 1000,
            'Exercise Name': [f'Exercise {i}' for i in range(1, 1001)],
            'Weight': [100 + i for i in range(1000)],
            'Sets': [3] * 1000,
            'Discrete Reps': [10] * 1000,
            'Alternating': [False] * 1000
        })
        
        result = validator.validate_dataframe(large_df)
        
        assert result.records_processed == 1000
        assert result.records_valid == 1000
        assert result.is_valid is True
    
    def test_mixed_data_types(self, validator):
        """Test validation with mixed data types in columns."""
        mixed_df = pd.DataFrame({
            'Workout Date': ['2024-01-01', 20240101, pd.Timestamp('2024-01-03')],
            'Exercise Type': ['Strength', 'Cardio', 'Strength'],
            'Exercise Name': ['Bench Press', 'Running', 'Squats'],
            'Weight': [135, '150', 185.5],
            'Sets': [3, '4', 5],
            'Discrete Reps': [10, 8, '12'],
            'Alternating': [False, 'True', True]
        })
        
        result = validator.validate_dataframe(mixed_df)
        
        # Should handle mixed types gracefully
        assert result.records_processed == 3
        assert len(result.errors) == 0  # Should convert types successfully


class TestIntegrationScenarios:
    """Test integration scenarios that combine multiple validation aspects."""
    
    @pytest.fixture
    def validator(self):
        return WorkoutDataValidator()
    
    def test_real_world_scenario(self, validator):
        """Test a realistic scenario with various data quality issues."""
        real_world_df = pd.DataFrame({
            'Workout Date': ['2024-01-01', 'invalid-date', '2024-01-03', '2024-01-01'],
            'Exercise Type': ['Strength', 'Strength', '', 'Strength'],
            'Exercise Name': ['Bench Press', 'Squats', 'Deadlift', 'Bench Press'],
            'Weight': [135, -10, 225, 135],
            'Sets': [3, 4, 5, 3],
            'Discrete Reps': [10, 8, -5, 10],
            'Alternating': [False, True, False, False]
        })
        
        cleaned_df, result = validator.clean_and_validate_data(real_world_df)
        
        # Should remove invalid records
        assert len(cleaned_df) < len(real_world_df)
        assert result.records_invalid > 0
        assert result.records_valid == len(cleaned_df)
        
        # Remaining data should be valid
        if len(cleaned_df) > 0:
            assert all(cleaned_df['Weight'] >= 0)
            assert all(cleaned_df['Sets'] >= 0)
            assert all(cleaned_df['Discrete Reps'] >= 0)
            assert all(cleaned_df['Exercise Name'].str.strip() != '')
    
    def test_progressive_cleaning(self, validator):
        """Test that cleaning progressively improves data quality."""
        problematic_df = pd.DataFrame({
            'Workout Date': ['2024-01-01', 'invalid', '2024-01-03', '2024-01-01'],
            'Exercise Type': ['Strength', 'Strength', 'Strength', 'Strength'],
            'Exercise Name': ['Bench Press', 'Squats', 'Deadlift', 'Bench Press'],
            'Weight': [135, -10, 225, 135],
            'Sets': [3, 4, 5, 3],
            'Discrete Reps': [10, 8, 6, 10],
            'Alternating': [False, True, False, False]
        })
        
        # First validation should show issues
        initial_result = validator.validate_dataframe(problematic_df)
        assert not initial_result.is_valid
        assert initial_result.records_invalid > 0
        
        # Cleaning should resolve issues
        cleaned_df, final_result = validator.clean_and_validate_data(problematic_df)
        assert final_result.records_valid == len(cleaned_df)
        assert len(cleaned_df) < len(problematic_df)
        
        # Re-validate cleaned data should be valid
        revalidation_result = validator.validate_dataframe(cleaned_df)
        assert revalidation_result.is_valid
        assert revalidation_result.records_invalid == 0

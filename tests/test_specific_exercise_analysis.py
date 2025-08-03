"""
Test suite for the specific exercise analysis module.

This module tests the specific exercise analysis functionality including:
- Filtering data by specific exercise name
- Calculating maximum statistics for selected exercises
- Handling cases where no data exists for selected exercises
- Error handling and edge cases
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import logging

from src.backend.specific_exercise_analysis import (
    analyze_specific_exercise,
    get_exercise_time_series,
    get_exercise_max_statistics
)


class TestSpecificExerciseAnalysis:
    """Test suite for specific exercise analysis functionality."""
    
    def setup_method(self):
        """Set up test fixtures for each test method."""
        # Configure logging for testing
        logging.basicConfig(level=logging.INFO)
    
    def teardown_method(self):
        """Clean up after each test method."""
        pass
    
    def test_analyze_specific_exercise_normal_operation(self, sample_workout_data):
        """
        Test normal operation of analyze_specific_exercise with valid input data.
        
        Verifies:
        - Filters data by specific exercise name
        - Calculates maximum statistics correctly
        - Returns expected structure
        """
        # Arrange
        df_input = sample_workout_data.copy()
        exercise_name = "Bench Press"
        
        # Act
        result = analyze_specific_exercise(exercise_name, df_input)
        
        # Assert
        assert isinstance(result, dict)
        assert 'filtered_data' in result
        assert 'max_statistics' in result
        assert 'exercise_found' in result
        assert 'total_records' in result
        
        assert result['exercise_found'] is True
        assert result['total_records'] == 3  # 3 Bench Press records
        
        # Check filtered data
        filtered_df = result['filtered_data']
        assert isinstance(filtered_df, pd.DataFrame)
        assert len(filtered_df) == 3
        assert all('Bench Press' in name for name in filtered_df['detailed_exercise_name'])
        
        # Check max statistics
        max_stats = result['max_statistics']
        assert 'max_weight' in max_stats
        assert 'max_reps' in max_stats
        assert 'max_sets' in max_stats
        assert 'max_volume' in max_stats
        
        # Verify max weight calculation
        assert max_stats['max_weight']['value'] == 155.0  # Max weight in sample data
        assert 'date' in max_stats['max_weight']
    
    def test_analyze_specific_exercise_case_insensitive(self, sample_workout_data):
        """
        Test that exercise name matching is case-insensitive.
        
        Verifies:
        - Function matches exercise names regardless of case
        - Returns same results for different case variations
        """
        # Arrange
        df_input = sample_workout_data.copy()
        exercise_name_variations = ["bench press", "BENCH PRESS", "Bench Press", "bench Press"]
        
        # Act & Assert
        for exercise_name in exercise_name_variations:
            result = analyze_specific_exercise(exercise_name, df_input)
            assert result['exercise_found'] is True
            assert result['total_records'] == 3
    
    def test_analyze_specific_exercise_not_found(self, sample_workout_data):
        """
        Test behavior when exercise is not found in data.
        
        Verifies:
        - Function handles missing exercise gracefully
        - Returns appropriate empty results
        """
        # Arrange
        df_input = sample_workout_data.copy()
        exercise_name = "Non-existent Exercise"
        
        # Act
        result = analyze_specific_exercise(exercise_name, df_input)
        
        # Assert
        assert result['exercise_found'] is False
        assert result['total_records'] == 0
        assert result['filtered_data'].empty
        assert result['max_statistics'] == {}
    
    def test_analyze_specific_exercise_empty_dataframe(self):
        """
        Test behavior with empty DataFrame.
        
        Verifies:
        - Function handles empty DataFrame gracefully
        - Returns appropriate empty results
        """
        # Arrange
        df_input = pd.DataFrame(columns=['detailed_exercise_name', 'weight', 'sets', 'reps', 'workout_date'])
        exercise_name = "Bench Press"
        
        # Act
        result = analyze_specific_exercise(exercise_name, df_input)
        
        # Assert
        assert result['exercise_found'] is False
        assert result['total_records'] == 0
        assert result['filtered_data'].empty
        assert result['max_statistics'] == {}
    
    def test_analyze_specific_exercise_invalid_exercise_name(self, sample_workout_data):
        """
        Test behavior with invalid exercise name.
        
        Verifies:
        - Function raises ValueError for empty or None exercise names
        - Proper error handling for invalid inputs
        """
        # Arrange
        df_input = sample_workout_data.copy()
        invalid_names = ["", "   ", None]
        
        # Act & Assert
        for exercise_name in invalid_names:
            with pytest.raises(ValueError) as exc_info:
                analyze_specific_exercise(exercise_name, df_input)
            assert "exercise_name must be a non-empty string" in str(exc_info.value)
    
    def test_analyze_specific_exercise_invalid_dataframe(self):
        """
        Test behavior with invalid DataFrame input.
        
        Verifies:
        - Function raises ValueError for non-DataFrame inputs
        - Proper error handling for invalid inputs
        """
        # Arrange
        invalid_inputs = [None, "not a dataframe", 123, []]
        exercise_name = "Bench Press"
        
        # Act & Assert
        for df_input in invalid_inputs:
            with pytest.raises(ValueError) as exc_info:
                analyze_specific_exercise(exercise_name, df_input)
            assert "df must be a pandas DataFrame" in str(exc_info.value)
    
    def test_analyze_specific_exercise_missing_columns(self, sample_workout_data):
        """
        Test behavior when required columns are missing.
        
        Verifies:
        - Function raises ValueError for missing required columns
        - Proper error handling for incomplete data
        """
        # Arrange
        df_input = sample_workout_data.copy()
        df_input = df_input.drop(columns=['detailed_exercise_name'])
        exercise_name = "Bench Press"
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            analyze_specific_exercise(exercise_name, df_input)
        assert "Missing required columns" in str(exc_info.value)
    
    def test_analyze_specific_exercise_single_record(self):
        """
        Test behavior with single record for an exercise.
        
        Verifies:
        - Function works correctly with minimal data
        - All statistics are calculated correctly
        """
        # Arrange
        df_input = pd.DataFrame({
            'detailed_exercise_name': ['Bench Press'],
            'weight': [135],
            'sets': [3],
            'reps': [10],
            'alternating': [False],
            'workout_date': [datetime.now()]
        })
        exercise_name = "Bench Press"
        
        # Act
        result = analyze_specific_exercise(exercise_name, df_input)
        
        # Assert
        assert result['exercise_found'] is True
        assert result['total_records'] == 1
        assert result['max_statistics']['max_weight']['value'] == 135.0
        assert result['max_statistics']['max_reps']['value'] == 10
        assert result['max_statistics']['max_sets']['value'] == 3
        assert result['max_statistics']['max_volume']['value'] == 4050.0  # 135 * 3 * 10
    
    def test_analyze_specific_exercise_with_null_values(self, sample_workout_data):
        """
        Test behavior with null values in data.
        
        Verifies:
        - Function handles null values gracefully
        - Statistics are calculated correctly despite nulls
        """
        # Arrange
        df_input = sample_workout_data.copy()
        df_input.loc[0, 'weight'] = np.nan
        df_input.loc[1, 'reps'] = np.nan
        exercise_name = "Bench Press"
        
        # Act
        result = analyze_specific_exercise(exercise_name, df_input)
        
        # Assert
        assert result['exercise_found'] is True
        # Should still calculate max statistics for non-null values
        assert 'max_weight' in result['max_statistics']
        assert 'max_reps' in result['max_statistics']
    
    def test_analyze_specific_exercise_all_null_values(self):
        """
        Test behavior when all values for a statistic are null.
        
        Verifies:
        - Function handles all-null columns gracefully
        - Statistics are not calculated for all-null columns
        """
        # Arrange
        df_input = pd.DataFrame({
            'detailed_exercise_name': ['Bench Press', 'Bench Press'],
            'weight': [np.nan, np.nan],
            'sets': [3, 3],
            'reps': [10, 10],
            'alternating': [False, False],
            'workout_date': [datetime.now(), datetime.now()]
        })
        exercise_name = "Bench Press"
        
        # Act
        result = analyze_specific_exercise(exercise_name, df_input)
        
        # Assert
        assert result['exercise_found'] is True
        assert 'max_weight' not in result['max_statistics']  # Should not calculate max weight
        assert 'max_reps' in result['max_statistics']  # Should calculate max reps
        assert 'max_sets' in result['max_statistics']  # Should calculate max sets
    
    def test_analyze_specific_exercise_date_formatting(self, sample_workout_data):
        """
        Test that dates are formatted correctly in max statistics.
        
        Verifies:
        - Dates are returned in YYYY-MM-DD format
        - Date formatting works for different date types
        """
        # Arrange
        df_input = sample_workout_data.copy()
        exercise_name = "Bench Press"
        
        # Act
        result = analyze_specific_exercise(exercise_name, df_input)
        
        # Assert
        max_stats = result['max_statistics']
        for stat_name, stat_data in max_stats.items():
            assert 'date' in stat_data
            # Check that date is in YYYY-MM-DD format
            date_str = stat_data['date']
            assert len(date_str) == 10  # YYYY-MM-DD format
            assert date_str.count('-') == 2
    
    def test_analyze_specific_exercise_sorted_by_date(self, sample_workout_data):
        """
        Test that filtered data is sorted by date.
        
        Verifies:
        - Filtered data is sorted chronologically
        - Time series analysis is properly ordered
        """
        # Arrange
        df_input = sample_workout_data.copy()
        exercise_name = "Bench Press"
        
        # Act
        result = analyze_specific_exercise(exercise_name, df_input)
        
        # Assert
        filtered_df = result['filtered_data']
        # Check that dates are sorted (ascending)
        dates = pd.to_datetime(filtered_df['workout_date'])
        assert dates.is_monotonic_increasing
    
    def test_analyze_specific_exercise_volume_calculation(self, sample_workout_data):
        """
        Test that volume is calculated correctly when not present.
        
        Verifies:
        - Volume is calculated as weight * sets * reps
        - Volume calculation works correctly
        """
        # Arrange
        df_input = sample_workout_data.copy()
        # Remove volume column if it exists
        if 'volume' in df_input.columns:
            df_input = df_input.drop(columns=['volume'])
        exercise_name = "Bench Press"
        
        # Act
        result = analyze_specific_exercise(exercise_name, df_input)
        
        # Assert
        filtered_df = result['filtered_data']
        assert 'volume' in filtered_df.columns
        
        # Check volume calculation - data is sorted by date, so order may vary
        # Calculate expected volumes for each row
        expected_volumes = []
        for _, row in filtered_df.iterrows():
            expected_volume = row['weight'] * row['sets'] * row['reps']
            expected_volumes.append(expected_volume)
        
        actual_volumes = filtered_df['volume'].tolist()
        assert actual_volumes == expected_volumes
    
    def test_get_exercise_time_series(self, sample_workout_data):
        """
        Test get_exercise_time_series function.
        
        Verifies:
        - Function returns filtered DataFrame
        - Function handles errors gracefully
        """
        # Arrange
        df_input = sample_workout_data.copy()
        exercise_name = "Bench Press"
        
        # Act
        result = get_exercise_time_series(exercise_name, df_input)
        
        # Assert
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert all('Bench Press' in name for name in result['detailed_exercise_name'])
    
    def test_get_exercise_time_series_not_found(self, sample_workout_data):
        """
        Test get_exercise_time_series when exercise not found.
        
        Verifies:
        - Function returns empty DataFrame when exercise not found
        """
        # Arrange
        df_input = sample_workout_data.copy()
        exercise_name = "Non-existent Exercise"
        
        # Act
        result = get_exercise_time_series(exercise_name, df_input)
        
        # Assert
        assert isinstance(result, pd.DataFrame)
        assert result.empty
    
    def test_get_exercise_max_statistics(self, sample_workout_data):
        """
        Test get_exercise_max_statistics function.
        
        Verifies:
        - Function returns max statistics dictionary
        - Function handles errors gracefully
        """
        # Arrange
        df_input = sample_workout_data.copy()
        exercise_name = "Bench Press"
        
        # Act
        result = get_exercise_max_statistics(exercise_name, df_input)
        
        # Assert
        assert isinstance(result, dict)
        assert 'max_weight' in result
        assert 'max_reps' in result
        assert 'max_sets' in result
        assert 'max_volume' in result
    
    def test_get_exercise_max_statistics_not_found(self, sample_workout_data):
        """
        Test get_exercise_max_statistics when exercise not found.
        
        Verifies:
        - Function returns empty dictionary when exercise not found
        """
        # Arrange
        df_input = sample_workout_data.copy()
        exercise_name = "Non-existent Exercise"
        
        # Act
        result = get_exercise_max_statistics(exercise_name, df_input)
        
        # Assert
        assert isinstance(result, dict)
        assert result == {}
    
    def test_analyze_specific_exercise_with_whitespace(self, sample_workout_data):
        """
        Test that function handles whitespace in exercise names.
        
        Verifies:
        - Function trims whitespace from exercise names
        - Matching works with leading/trailing spaces
        """
        # Arrange
        df_input = sample_workout_data.copy()
        exercise_name = "  Bench Press  "
        
        # Act
        result = analyze_specific_exercise(exercise_name, df_input)
        
        # Assert
        assert result['exercise_found'] is True
        assert result['total_records'] == 3
    
    def test_analyze_specific_exercise_performance_large_dataset(self, large_workout_dataset):
        """
        Test performance with large dataset.
        
        Verifies:
        - Function performs efficiently with large datasets
        - No memory issues with large data
        """
        # Arrange
        df_input = large_workout_dataset.copy()
        exercise_name = "Bench Press"
        
        # Act
        import time
        start_time = time.time()
        result = analyze_specific_exercise(exercise_name, df_input)
        end_time = time.time()
        
        # Assert
        assert isinstance(result, dict)
        assert 'filtered_data' in result
        assert 'max_statistics' in result
        assert (end_time - start_time) < 5.0  # Should complete within 5 seconds
    
    def test_analyze_specific_exercise_exception_handling(self):
        """
        Test exception handling in analyze_specific_exercise.
        
        Verifies:
        - Function handles unexpected exceptions gracefully
        - Proper error logging
        """
        # Arrange - Create DataFrame that will cause an exception
        df_input = pd.DataFrame({
            'detailed_exercise_name': ['Bench Press'],
            'weight': ['invalid_weight'],  # String instead of number
            'sets': [3],
            'reps': [10],
            'alternating': [False],
            'workout_date': [datetime.now()]
        })
        exercise_name = "Bench Press"
        
        # Act & Assert
        with pytest.raises(Exception):
            analyze_specific_exercise(exercise_name, df_input)
    
    def test_analyze_specific_exercise_with_malicious_input(self, sample_malicious_data):
        """
        Test with malicious input data.
        
        Verifies:
        - Function handles malicious input safely
        - No security vulnerabilities are exploited
        """
        # Arrange
        df_input = sample_malicious_data.copy()
        exercise_name = "'; DROP TABLE exercises; --"
        
        # Act
        result = analyze_specific_exercise(exercise_name, df_input)
        
        # Assert
        assert isinstance(result, dict)
        # The malicious exercise name exists in the sample data, so it should be found
        assert result['exercise_found'] is True
        assert result['total_records'] == 1
        # Verify that the function handles the malicious input safely
        assert 'max_statistics' in result
        assert 'filtered_data' in result
    
    def test_analyze_specific_exercise_data_types(self):
        """
        Test with various data types.
        
        Verifies:
        - Function handles different data types correctly
        - Type conversions work as expected
        """
        # Arrange
        df_input = pd.DataFrame({
            'detailed_exercise_name': ['Bench Press', 'Bench Press'],
            'weight': [135.0, 145],  # Mix of float and int
            'sets': [3, 3],
            'reps': [10, 12],
            'alternating': [False, True],
            'workout_date': [datetime.now(), datetime.now()]
        })
        exercise_name = "Bench Press"
        
        # Act
        result = analyze_specific_exercise(exercise_name, df_input)
        
        # Assert
        assert result['exercise_found'] is True
        max_stats = result['max_statistics']
        assert isinstance(max_stats['max_weight']['value'], float)
        assert isinstance(max_stats['max_reps']['value'], int)
        assert isinstance(max_stats['max_sets']['value'], int)
    
    def test_analyze_specific_exercise_edge_cases(self, sample_edge_case_data):
        """
        Test with edge case data.
        
        Verifies:
        - Function handles edge cases correctly
        - Boundary conditions are handled properly
        """
        # Arrange
        df_input = sample_edge_case_data.copy()
        exercise_name = "A"
        
        # Act
        result = analyze_specific_exercise(exercise_name, df_input)
        
        # Assert
        assert result['exercise_found'] is True
        assert result['total_records'] == 1
        max_stats = result['max_statistics']
        assert 'max_weight' in max_stats
        assert 'max_reps' in max_stats
        assert 'max_sets' in max_stats
    
    @pytest.mark.slow
    def test_analyze_specific_exercise_stress_test(self):
        """
        Stress test for analyze_specific_exercise with extreme data.
        
        Verifies:
        - Function handles extreme data sizes
        - Performance remains acceptable
        """
        # Arrange - Create very large dataset
        n_records = 10000
        df_input = pd.DataFrame({
            'detailed_exercise_name': ['Bench Press'] * n_records,
            'weight': np.random.randint(50, 500, n_records),
            'sets': np.random.randint(1, 5, n_records),
            'reps': np.random.randint(5, 20, n_records),
            'alternating': np.random.choice([True, False], n_records),
            'workout_date': [datetime.now()] * n_records
        })
        exercise_name = "Bench Press"
        
        # Act
        import time
        start_time = time.time()
        result = analyze_specific_exercise(exercise_name, df_input)
        end_time = time.time()
        
        # Assert
        assert isinstance(result, dict)
        assert result['exercise_found'] is True
        assert result['total_records'] == n_records
        assert (end_time - start_time) < 10.0  # Should complete within 10 seconds
    
    def test_analyze_specific_exercise_logging(self, caplog):
        """
        Test that analyze_specific_exercise logs appropriate messages.
        
        Verifies:
        - Function logs info messages for successful operations
        - Function logs error messages for failures
        """
        # Arrange
        df_input = pd.DataFrame({
            'detailed_exercise_name': ['Bench Press'],
            'weight': [135],
            'sets': [3],
            'reps': [10],
            'alternating': [False],
            'workout_date': [datetime.now()]
        })
        exercise_name = "Bench Press"
        
        # Act
        with caplog.at_level(logging.INFO):
            result = analyze_specific_exercise(exercise_name, df_input)
        
        # Assert
        assert "Successfully analyzed exercise: Bench Press with 1 records" in caplog.text
    
    def test_analyze_specific_exercise_error_logging(self, caplog):
        """
        Test error logging in analyze_specific_exercise.
        
        Verifies:
        - Function logs error messages for failures
        - Error messages are descriptive
        """
        # Arrange
        df_input = pd.DataFrame({
            'detailed_exercise_name': ['Bench Press'],
            'weight': [135],
            'sets': [3],
            'reps': [10],
            'alternating': [False],
            'workout_date': [datetime.now()]
        })
        exercise_name = ""
        
        # Act
        with caplog.at_level(logging.ERROR):
            with pytest.raises(ValueError):
                analyze_specific_exercise(exercise_name, df_input)
        
        # Assert
        assert "exercise_name must be a non-empty string" in caplog.text
    
    def test_get_exercise_time_series_exception_handling(self, caplog):
        """
        Test exception handling in get_exercise_time_series.
        
        Verifies:
        - Function handles exceptions gracefully
        - Returns empty DataFrame on exception
        - Logs error appropriately
        """
        # Arrange
        df_input = pd.DataFrame({
            'detailed_exercise_name': ['Bench Press'],
            'weight': ['invalid_weight'],  # String instead of number
            'sets': [3],
            'reps': [10],
            'alternating': [False],
            'workout_date': [datetime.now()]
        })
        exercise_name = "Bench Press"
        
        # Act
        with caplog.at_level(logging.ERROR):
            result = get_exercise_time_series(exercise_name, df_input)
        
        # Assert
        assert isinstance(result, pd.DataFrame)
        assert result.empty
        assert "Error getting time series for exercise" in caplog.text
    
    def test_get_exercise_max_statistics_exception_handling(self, caplog):
        """
        Test exception handling in get_exercise_max_statistics.
        
        Verifies:
        - Function handles exceptions gracefully
        - Returns empty dictionary on exception
        - Logs error appropriately
        """
        # Arrange
        df_input = pd.DataFrame({
            'detailed_exercise_name': ['Bench Press'],
            'weight': ['invalid_weight'],  # String instead of number
            'sets': [3],
            'reps': [10],
            'alternating': [False],
            'workout_date': [datetime.now()]
        })
        exercise_name = "Bench Press"
        
        # Act
        with caplog.at_level(logging.ERROR):
            result = get_exercise_max_statistics(exercise_name, df_input)
        
        # Assert
        assert isinstance(result, dict)
        assert result == {}
        assert "Error getting max statistics for exercise" in caplog.text 
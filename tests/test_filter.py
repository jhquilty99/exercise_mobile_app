"""
Tests for the filter module functionality.

This module tests the data filtering capabilities including timeframe filtering,
error handling, edge cases, and performance considerations.
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
import numpy as np

from src.backend.filter import filter_dataframe_by_timeframe


class TestFilterDataframeByTimeframe:
    """Test suite for filter_dataframe_by_timeframe functionality."""
    
    def setup_method(self):
        """Set up test fixtures for each test method."""
        pass
    
    def teardown_method(self):
        """Clean up after each test method."""
        pass
    
    def test_all_time_timeframe(self, sample_workout_data):
        """Test filtering with 'All time' timeframe returns unfiltered data."""
        # Arrange
        df = sample_workout_data
        
        # Act
        result = filter_dataframe_by_timeframe(df, "All time")
        
        # Assert
        assert len(result) == len(df)
        pd.testing.assert_frame_equal(result, df)
    
    def test_last_7_days_timeframe(self, sample_workout_data):
        """Test filtering with 'Last 7 days' timeframe."""
        # Arrange
        df = sample_workout_data
        
        # Act
        result = filter_dataframe_by_timeframe(df, "Last 7 days")
        
        # Assert
        assert len(result) <= len(df)
        # All dates should be within last 7 days
        cutoff_date = datetime.now() - timedelta(days=7)
        for date in result['workout_date']:
            assert date >= cutoff_date
    
    def test_last_30_days_timeframe(self, sample_workout_data):
        """Test filtering with 'Last 30 days' timeframe."""
        # Arrange
        df = sample_workout_data
        
        # Act
        result = filter_dataframe_by_timeframe(df, "Last 30 days")
        
        # Assert
        assert len(result) <= len(df)
        # All dates should be within last 30 days
        cutoff_date = datetime.now() - timedelta(days=30)
        for date in result['workout_date']:
            assert date >= cutoff_date
    
    def test_last_3_months_timeframe(self, sample_workout_data):
        """Test filtering with 'Last 3 months' timeframe."""
        # Arrange
        df = sample_workout_data
        
        # Act
        result = filter_dataframe_by_timeframe(df, "Last 3 months")
        
        # Assert
        assert len(result) <= len(df)
        # All dates should be within last 90 days
        cutoff_date = datetime.now() - timedelta(days=90)
        for date in result['workout_date']:
            assert date >= cutoff_date
    
    def test_last_6_months_timeframe(self, sample_workout_data):
        """Test filtering with 'Last 6 months' timeframe."""
        # Arrange
        df = sample_workout_data
        
        # Act
        result = filter_dataframe_by_timeframe(df, "Last 6 months")
        
        # Assert
        assert len(result) <= len(df)
        # All dates should be within last 180 days
        cutoff_date = datetime.now() - timedelta(days=180)
        for date in result['workout_date']:
            assert date >= cutoff_date
    
    def test_last_year_timeframe(self, sample_workout_data):
        """Test filtering with 'Last year' timeframe."""
        # Arrange
        df = sample_workout_data
        
        # Act
        result = filter_dataframe_by_timeframe(df, "Last year")
        
        # Assert
        assert len(result) <= len(df)
        # All dates should be within last 365 days
        cutoff_date = datetime.now() - timedelta(days=365)
        for date in result['workout_date']:
            assert date >= cutoff_date
    
    def test_unknown_timeframe_returns_unfiltered(self, sample_workout_data):
        """Test that unknown timeframe returns unfiltered dataframe."""
        # Arrange
        df = sample_workout_data
        
        # Act
        result = filter_dataframe_by_timeframe(df, "Unknown timeframe")
        
        # Assert
        assert len(result) == len(df)
        pd.testing.assert_frame_equal(result, df)
    
    def test_empty_dataframe_handling(self, sample_empty_data):
        """Test filtering with empty dataframe."""
        # Arrange
        df = sample_empty_data
        
        # Act
        result = filter_dataframe_by_timeframe(df, "Last 7 days")
        
        # Assert
        assert len(result) == 0
        assert list(result.columns) == list(df.columns)
    
    def test_single_record_dataframe(self, sample_minimal_data):
        """Test filtering with single record dataframe."""
        # Arrange
        df = sample_minimal_data
        
        # Act
        result = filter_dataframe_by_timeframe(df, "Last 7 days")
        
        # Assert
        assert len(result) <= len(df)
        if len(result) > 0:
            cutoff_date = datetime.now() - timedelta(days=7)
            assert result['workout_date'].iloc[0] >= cutoff_date
    
    def test_large_dataset_performance(self, large_workout_dataset):
        """Test performance with large dataset."""
        # Arrange
        df = large_workout_dataset
        
        # Act & Assert - should complete without error
        result = filter_dataframe_by_timeframe(df, "Last 30 days")
        assert len(result) <= len(df)
    
    def test_edge_case_dates(self, sample_edge_case_data):
        """Test filtering with edge case dates."""
        # Arrange
        df = sample_edge_case_data
        
        # Act
        result = filter_dataframe_by_timeframe(df, "Last 7 days")
        
        # Assert
        assert len(result) <= len(df)
        if len(result) > 0:
            cutoff_date = datetime.now() - timedelta(days=7)
            for date in result['workout_date']:
                assert date >= cutoff_date
    
    def test_mixed_date_ranges(self):
        """Test filtering with data spanning multiple timeframes."""
        # Arrange
        dates = [
            datetime.now() - timedelta(days=1),   # Recent
            datetime.now() - timedelta(days=5),   # Recent
            datetime.now() - timedelta(days=10),  # Recent
            datetime.now() - timedelta(days=20),  # Older
            datetime.now() - timedelta(days=50),  # Much older
            datetime.now() - timedelta(days=100), # Very old
        ]
        
        df = pd.DataFrame({
            'detailed_exercise_name': ['Bench Press'] * 6,
            'weight': [135] * 6,
            'sets': [3] * 6,
            'reps': [10] * 6,
            'alternating': [False] * 6,
            'workout_date': dates
        })
        
        # Act & Assert for different timeframes
        result_7_days = filter_dataframe_by_timeframe(df, "Last 7 days")
        assert len(result_7_days) == 2  # Only 2 records within 7 days
        
        result_30_days = filter_dataframe_by_timeframe(df, "Last 30 days")
        assert len(result_30_days) == 4  # 4 records within 30 days
    
    def test_invalid_dataframe_handling(self):
        """Test handling of invalid dataframe input."""
        # Arrange
        invalid_df = pd.DataFrame({
            'wrong_column': [1, 2, 3],
            'another_wrong_column': ['a', 'b', 'c']
        })
        
        # Act
        result = filter_dataframe_by_timeframe(invalid_df, "Last 7 days")
        
        # Assert - should return empty dataframe with original columns
        assert len(result) == 0
        assert list(result.columns) == list(invalid_df.columns)
    
    def test_missing_workout_date_column(self):
        """Test handling when workout_date column is missing."""
        # Arrange
        df_without_date = pd.DataFrame({
            'detailed_exercise_name': ['Bench Press', 'Squat'],
            'weight': [135, 185],
            'sets': [3, 3],
            'reps': [10, 8],
            'alternating': [False, False]
        })
        
        # Act
        result = filter_dataframe_by_timeframe(df_without_date, "Last 7 days")
        
        # Assert - should return empty dataframe with original columns
        assert len(result) == 0
        assert list(result.columns) == list(df_without_date.columns)
    
    def test_none_dataframe_handling(self):
        """Test handling of None dataframe input."""
        # Act
        result = filter_dataframe_by_timeframe(None, "Last 7 days")
        
        # Assert - should return empty dataframe
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    def test_none_timeframe_handling(self, sample_workout_data):
        """Test handling of None timeframe input."""
        # Arrange
        df = sample_workout_data
        
        # Act
        result = filter_dataframe_by_timeframe(df, None)
        
        # Assert - should return unfiltered dataframe
        assert len(result) == len(df)
        pd.testing.assert_frame_equal(result, df)
    
    def test_empty_string_timeframe_handling(self, sample_workout_data):
        """Test handling of empty string timeframe input."""
        # Arrange
        df = sample_workout_data
        
        # Act
        result = filter_dataframe_by_timeframe(df, "")
        
        # Assert - should return unfiltered dataframe
        assert len(result) == len(df)
        pd.testing.assert_frame_equal(result, df)
    
    @pytest.mark.slow
    def test_performance_with_very_large_dataset(self):
        """Performance test with very large dataset."""
        # Arrange
        n_records = 10000
        exercises = ['Bench Press', 'Squat', 'Deadlift', 'Overhead Press', 'Row']
        
        large_df = pd.DataFrame({
            'detailed_exercise_name': np.random.choice(exercises, n_records),
            'weight': np.random.randint(50, 500, n_records),
            'sets': np.random.randint(1, 5, n_records),
            'reps': np.random.randint(5, 20, n_records),
            'alternating': np.random.choice([True, False], n_records),
            'workout_date': [
                datetime.now() - timedelta(days=i) for i in range(n_records)
            ]
        })
        
        # Act & Assert - should complete within reasonable time
        import time
        start_time = time.time()
        result = filter_dataframe_by_timeframe(large_df, "Last 30 days")
        end_time = time.time()
        
        assert len(result) <= len(large_df)
        assert (end_time - start_time) < 1.0  # Should complete within 1 second
    
    def test_case_sensitivity_timeframe(self, sample_workout_data):
        """Test that timeframe filtering is case sensitive."""
        # Arrange
        df = sample_workout_data
        
        # Act
        result_lowercase = filter_dataframe_by_timeframe(df, "last 7 days")
        result_uppercase = filter_dataframe_by_timeframe(df, "LAST 7 DAYS")
        
        # Assert - should return unfiltered data for non-matching cases
        assert len(result_lowercase) == len(df)
        assert len(result_uppercase) == len(df)
    
    def test_whitespace_handling_timeframe(self, sample_workout_data):
        """Test handling of timeframes with extra whitespace."""
        # Arrange
        df = sample_workout_data
        
        # Act
        result_with_spaces = filter_dataframe_by_timeframe(df, "  Last 7 days  ")
        result_with_tabs = filter_dataframe_by_timeframe(df, "\tLast 7 days\t")
        
        # Assert - should return unfiltered data for non-matching cases
        assert len(result_with_spaces) == len(df)
        assert len(result_with_tabs) == len(df)
    
    def test_malicious_input_handling(self, sample_malicious_data):
        """Test handling of malicious input data."""
        # Arrange
        df = sample_malicious_data
        
        # Act
        result = filter_dataframe_by_timeframe(df, "Last 7 days")
        
        # Assert - should handle malicious data gracefully
        assert isinstance(result, pd.DataFrame)
        assert len(result) <= len(df)
    
    def test_invalid_date_handling(self):
        """Test handling of invalid dates in dataframe."""
        # Arrange
        df_with_invalid_dates = pd.DataFrame({
            'detailed_exercise_name': ['Bench Press', 'Squat', 'Deadlift'],
            'weight': [135, 185, 225],
            'sets': [3, 3, 3],
            'reps': [10, 8, 5],
            'alternating': [False, False, False],
            'workout_date': [
                datetime.now() - timedelta(days=1),
                None,  # Invalid date
                datetime.now() - timedelta(days=3)
            ]
        })
        
        # Act
        result = filter_dataframe_by_timeframe(df_with_invalid_dates, "Last 7 days")
        
        # Assert - should handle invalid dates gracefully
        assert isinstance(result, pd.DataFrame)
        assert len(result) <= len(df_with_invalid_dates)
    
    def test_future_date_handling(self):
        """Test handling of future dates in dataframe."""
        # Arrange
        df_with_future_dates = pd.DataFrame({
            'detailed_exercise_name': ['Bench Press', 'Squat', 'Deadlift'],
            'weight': [135, 185, 225],
            'sets': [3, 3, 3],
            'reps': [10, 8, 5],
            'alternating': [False, False, False],
            'workout_date': [
                datetime.now() - timedelta(days=1),
                datetime.now() + timedelta(days=1),  # Future date
                datetime.now() - timedelta(days=3)
            ]
        })
        
        # Act
        result = filter_dataframe_by_timeframe(df_with_future_dates, "Last 7 days")
        
        # Assert - should include future dates in "Last 7 days" filter
        assert isinstance(result, pd.DataFrame)
        assert len(result) <= len(df_with_future_dates)
    
    def test_all_timeframes_with_same_data(self, sample_workout_data):
        """Test all supported timeframes with the same dataset."""
        # Arrange
        df = sample_workout_data
        timeframes = [
            "All time",
            "Last 7 days", 
            "Last 30 days",
            "Last 3 months",
            "Last 6 months",
            "Last year"
        ]
        
        # Act & Assert
        for timeframe in timeframes:
            result = filter_dataframe_by_timeframe(df, timeframe)
            assert isinstance(result, pd.DataFrame)
            assert len(result) <= len(df)
            
            # Verify column structure is preserved
            assert list(result.columns) == list(df.columns)
    
    def test_data_integrity_preservation(self, sample_workout_data):
        """Test that filtering preserves data integrity."""
        # Arrange
        df = sample_workout_data
        
        # Act
        result = filter_dataframe_by_timeframe(df, "Last 7 days")
        
        # Assert
        if len(result) > 0:
            # Check that data types are preserved
            assert result['detailed_exercise_name'].dtype == df['detailed_exercise_name'].dtype
            assert result['weight'].dtype == df['weight'].dtype
            assert result['sets'].dtype == df['sets'].dtype
            assert result['reps'].dtype == df['reps'].dtype
            assert result['alternating'].dtype == df['alternating'].dtype
            assert result['workout_date'].dtype == df['workout_date'].dtype
            
            # Check that values are preserved (subset of original)
            for col in df.columns:
                if col != 'workout_date':  # workout_date is filtered
                    assert all(val in df[col].values for val in result[col].values)

"""
Test suite for all exercise statistics functionality.

Tests the analyze_all_exercises function and related functionality
as specified in BE-004: Exercise Frequency Analytics.

This test suite follows the testing standards outlined in testing_requirements.md
and provides comprehensive coverage for:
- Unit tests for all public methods
- Data validation tests
- Statistical accuracy tests
- Performance benchmarks
- Error handling for invalid data
- Edge cases and boundary conditions
- Security validation tests
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import time
import logging

from src.backend.all_exercise_statistics import (
    analyze_all_exercises,
    calculate_exercise_frequency,
    rank_exercises_by_frequency,
    calculate_percentage_breakdown,
    get_frequency_summary,
    WorkoutFrequencyAnalyzer,
    ExerciseRanking,
    FrequencyAnalysisResult
)
from src.backend.filter import filter_dataframe_by_timeframe


# Configure logging for tests
logger = logging.getLogger(__name__)


class TestAnalyzeAllExercises:
    """Test the main analyze_all_exercises function."""
    
    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.required_columns = ['exercise_name', 'weight_lbs', 'sets', 'discrete_reps', 'alternating', 'Workout Date']
    
    def teardown_method(self):
        """Clean up after each test method."""
        pass
    
    def test_analyze_all_exercises_count_metric(self, sample_dataframe):
        """Test analyzing exercises by count metric."""
        result = analyze_all_exercises(sample_dataframe, 'Count')
        
        assert isinstance(result, pd.DataFrame)
        assert 'rank' in result.columns
        assert 'exercise_name' in result.columns
        assert 'count' in result.columns
        
        # Check that exercises are ranked by count descending
        assert result.iloc[0]['exercise_name'] == 'Bench Press'
        assert result.iloc[0]['count'] == 3
        assert result.iloc[1]['exercise_name'] == 'Squat'
        assert result.iloc[1]['count'] == 2
        assert result.iloc[2]['exercise_name'] == 'Deadlift'
        assert result.iloc[2]['count'] == 1
    
    def test_analyze_all_exercises_max_weight_metric(self, sample_dataframe):
        """Test analyzing exercises by max weight metric."""
        result = analyze_all_exercises(sample_dataframe, 'Max Weight')
        
        assert isinstance(result, pd.DataFrame)
        assert 'rank' in result.columns
        assert 'exercise_name' in result.columns
        assert 'max_weight' in result.columns
        
        # Check that exercises are ranked by max weight descending
        assert result.iloc[0]['exercise_name'] == 'Deadlift'
        assert result.iloc[0]['max_weight'] == 225
        assert result.iloc[1]['exercise_name'] == 'Squat'
        assert result.iloc[1]['max_weight'] == 195
        assert result.iloc[2]['exercise_name'] == 'Bench Press'
        assert result.iloc[2]['max_weight'] == 155
    
    def test_analyze_all_exercises_average_reps_metric(self, sample_dataframe):
        """Test analyzing exercises by average reps metric."""
        result = analyze_all_exercises(sample_dataframe, 'Average Reps')
        
        assert isinstance(result, pd.DataFrame)
        assert 'rank' in result.columns
        assert 'exercise_name' in result.columns
        assert 'avg_reps' in result.columns
        
        # Check that exercises are ranked by average reps descending
        # Bench Press: (10 + 12 + 11) / 3 = 11.0
        # Squat: (8 + 6) / 2 = 7.0
        # Deadlift: 5.0
        assert result.iloc[0]['exercise_name'] == 'Bench Press'
        assert result.iloc[0]['avg_reps'] == 11.0
        assert result.iloc[1]['exercise_name'] == 'Squat'
        assert result.iloc[1]['avg_reps'] == 7.0
        assert result.iloc[2]['exercise_name'] == 'Deadlift'
        assert result.iloc[2]['avg_reps'] == 5.0
    
    def test_analyze_all_exercises_max_volume_metric(self, sample_dataframe):
        """Test analyzing exercises by max volume metric."""
        result = analyze_all_exercises(sample_dataframe, 'Max Volume')
        
        assert isinstance(result, pd.DataFrame)
        assert 'rank' in result.columns
        assert 'exercise_name' in result.columns
        assert 'max_volume' in result.columns
        
        # Check that exercises are ranked by max volume descending
        # Bench Press: max(135*3*10, 145*3*12, 155*3*11) = max(4050, 5220, 5115) = 5220
        # Squat: max(185*3*8, 195*3*6) = max(4440, 3510) = 4440
        # Deadlift: 225*3*5 = 3375
        assert result.iloc[0]['exercise_name'] == 'Bench Press'
        assert result.iloc[0]['max_volume'] == 5220
        assert result.iloc[1]['exercise_name'] == 'Squat'
        assert result.iloc[1]['max_volume'] == 4440
        assert result.iloc[2]['exercise_name'] == 'Deadlift'
        assert result.iloc[2]['max_volume'] == 3375
    
    def test_analyze_all_exercises_max_volume_with_alternating(self, sample_workout_data_alternating):
        """Test max volume calculation with alternating exercises."""
        result = analyze_all_exercises(sample_workout_data_alternating, 'Max Volume')
        
        assert isinstance(result, pd.DataFrame)
        
        # Check alternating exercise volume calculation
        # Dumbbell Curl: max(25*3*12/2, 30*3*10/2) = max(450, 450) = 450
        # Bench Press: 135*3*10 = 4050
        assert result.iloc[0]['exercise_name'] == 'Bench Press'
        assert result.iloc[0]['max_volume'] == 4050
        assert result.iloc[1]['exercise_name'] == 'Dumbbell Curl'
        assert result.iloc[1]['max_volume'] == 450
    
    def test_analyze_all_exercises_invalid_metric(self, sample_dataframe):
        """Test that invalid key metric raises ValueError."""
        with pytest.raises(ValueError, match="Invalid key metric"):
            analyze_all_exercises(sample_dataframe, 'Invalid Metric')
    
    def test_analyze_all_exercises_missing_columns(self):
        """Test that missing required columns raises ValueError."""
        df = pd.DataFrame({'exercise_name': ['Test']})
        
        with pytest.raises(ValueError, match="Required columns not found"):
            analyze_all_exercises(df, 'Count')
    
    def test_analyze_all_exercises_empty_dataframe(self, sample_empty_data):
        """Test with empty DataFrame."""
        result = analyze_all_exercises(sample_empty_data, 'Count')
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        assert 'rank' in result.columns
        assert 'exercise_name' in result.columns
        assert 'count' in result.columns
    
    @patch('src.backend.all_exercise_statistics.filter_dataframe_by_timeframe')
    def test_analyze_all_exercises_with_timeframe(self, mock_filter, sample_dataframe):
        """Test analyzing exercises with timeframe filtering."""
        # Mock the filter to return filtered data
        filtered_df = sample_dataframe.iloc[:3]  # Return first 3 rows
        mock_filter.return_value = filtered_df
        
        result = analyze_all_exercises(sample_dataframe, 'Count', 'Last 7 days')
        
        # Verify filter was called
        mock_filter.assert_called_once_with(sample_dataframe, 'Last 7 days')
        
        # Verify result is based on filtered data
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2  # Only 2 unique exercises in filtered data
    
    def test_analyze_all_exercises_all_time_timeframe(self, sample_dataframe):
        """Test that 'All time' timeframe doesn't apply filtering."""
        result = analyze_all_exercises(sample_dataframe, 'Count', 'All time')
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3  # All 3 unique exercises should be present


class TestCalculateExerciseFrequency:
    """Test the calculate_exercise_frequency function."""
    
    def test_calculate_exercise_frequency_basic(self):
        """Test basic frequency calculation."""
        data = {
            'exercise_name': ['Bench Press', 'Squat', 'Bench Press', 'Deadlift', 'Squat']
        }
        df = pd.DataFrame(data)
        
        result = calculate_exercise_frequency(df)
        
        assert isinstance(result, pd.DataFrame)
        assert 'exercise_name' in result.columns
        assert 'frequency' in result.columns
        
        # Check frequencies
        bench_press_row = result[result['exercise_name'] == 'Bench Press'].iloc[0]
        squat_row = result[result['exercise_name'] == 'Squat'].iloc[0]
        deadlift_row = result[result['exercise_name'] == 'Deadlift'].iloc[0]
        
        assert bench_press_row['frequency'] == 2
        assert squat_row['frequency'] == 2
        assert deadlift_row['frequency'] == 1
        
        # Check sorting (descending by frequency)
        assert result.iloc[0]['frequency'] >= result.iloc[1]['frequency']
        assert result.iloc[1]['frequency'] >= result.iloc[2]['frequency']
    
    def test_calculate_exercise_frequency_alternative_column_name(self):
        """Test frequency calculation with 'Exercise Name' column."""
        data = {
            'Exercise Name': ['Bench Press', 'Squat', 'Bench Press']
        }
        df = pd.DataFrame(data)
        
        result = calculate_exercise_frequency(df)
        
        assert isinstance(result, pd.DataFrame)
        assert 'exercise_name' in result.columns
        assert 'frequency' in result.columns
        
        # Check frequencies
        bench_press_row = result[result['exercise_name'] == 'Bench Press'].iloc[0]
        squat_row = result[result['exercise_name'] == 'Squat'].iloc[0]
        
        assert bench_press_row['frequency'] == 2
        assert squat_row['frequency'] == 1
    
    def test_calculate_exercise_frequency_no_exercise_column(self):
        """Test that missing exercise column raises ValueError."""
        df = pd.DataFrame({'other_column': ['test']})
        
        with pytest.raises(ValueError, match="No exercise name column found"):
            calculate_exercise_frequency(df)
    
    def test_calculate_exercise_frequency_empty_dataframe(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame(columns=['exercise_name'])
        
        result = calculate_exercise_frequency(df)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        assert 'exercise_name' in result.columns
        assert 'frequency' in result.columns


class TestRankExercisesByFrequency:
    """Test the rank_exercises_by_frequency function."""
    
    def test_rank_exercises_by_frequency_basic(self):
        """Test basic ranking functionality."""
        data = {
            'exercise_name': ['Bench Press', 'Squat', 'Bench Press', 'Deadlift', 'Squat']
        }
        df = pd.DataFrame(data)
        
        result = rank_exercises_by_frequency(df)
        
        assert isinstance(result, pd.DataFrame)
        assert 'rank' in result.columns
        assert 'exercise_name' in result.columns
        assert 'frequency' in result.columns
        assert 'percentage' in result.columns
        
        # Check ranking
        assert result.iloc[0]['rank'] == 1
        assert result.iloc[1]['rank'] == 2
        assert result.iloc[2]['rank'] == 3
        
        # Check percentages (total frequency = 5)
        bench_press_row = result[result['exercise_name'] == 'Bench Press'].iloc[0]
        squat_row = result[result['exercise_name'] == 'Squat'].iloc[0]
        deadlift_row = result[result['exercise_name'] == 'Deadlift'].iloc[0]
        
        assert bench_press_row['percentage'] == 40.0  # 2/5 * 100
        assert squat_row['percentage'] == 40.0  # 2/5 * 100
        assert deadlift_row['percentage'] == 20.0  # 1/5 * 100


class TestCalculatePercentageBreakdown:
    """Test the calculate_percentage_breakdown function."""
    
    def test_calculate_percentage_breakdown_basic(self):
        """Test basic percentage breakdown calculation."""
        data = {
            'exercise_name': ['Bench Press', 'Squat', 'Bench Press', 'Deadlift', 'Squat']
        }
        df = pd.DataFrame(data)
        
        result = calculate_percentage_breakdown(df)
        
        assert isinstance(result, dict)
        
        # Check percentages (total frequency = 5)
        assert result['Bench Press'] == 40.0  # 2/5 * 100
        assert result['Squat'] == 40.0  # 2/5 * 100
        assert result['Deadlift'] == 20.0  # 1/5 * 100


class TestGetFrequencySummary:
    """Test the get_frequency_summary function."""
    
    def test_get_frequency_summary_basic(self):
        """Test basic frequency summary calculation."""
        data = {
            'exercise_name': ['Bench Press', 'Squat', 'Bench Press', 'Deadlift', 'Squat']
        }
        df = pd.DataFrame(data)
        
        result = get_frequency_summary(df)
        
        assert isinstance(result, dict)
        assert 'total_exercises' in result
        assert 'total_workouts' in result
        assert 'most_frequent_exercise' in result
        assert 'most_frequent_count' in result
        assert 'average_frequency' in result
        assert 'median_frequency' in result
        assert 'min_frequency' in result
        assert 'max_frequency' in result
        
        # Check values
        assert result['total_exercises'] == 3
        assert result['total_workouts'] == 5
        assert result['most_frequent_exercise'] in ['Bench Press', 'Squat']  # Both have frequency 2
        assert result['most_frequent_count'] == 2
        assert result['min_frequency'] == 1
        assert result['max_frequency'] == 2


class TestWorkoutFrequencyAnalyzer:
    """Test the WorkoutFrequencyAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.analyzer = WorkoutFrequencyAnalyzer()
    
    def teardown_method(self):
        """Clean up after each test method."""
        pass
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        assert hasattr(self.analyzer, 'key_metrics')
        assert 'Max Volume' in self.analyzer.key_metrics
        assert 'Max Weight' in self.analyzer.key_metrics
        assert 'Average Reps' in self.analyzer.key_metrics
        assert 'Count' in self.analyzer.key_metrics
    
    def test_analyze_exercise_frequency(self, sample_dataframe):
        """Test comprehensive frequency analysis."""
        result = self.analyzer.analyze_exercise_frequency(sample_dataframe)
        
        assert isinstance(result, FrequencyAnalysisResult)
        assert result.total_exercises == 3
        assert result.total_workouts == 6
        assert 'unique_exercises' in result.analysis_summary
        assert 'most_frequent_exercise' in result.analysis_summary
        assert 'most_frequent_count' in result.analysis_summary
        assert 'average_frequency' in result.analysis_summary
        assert 'median_frequency' in result.analysis_summary
        assert 'total_workouts' in result.analysis_summary
        
        assert isinstance(result.frequency_data, pd.DataFrame)
        assert isinstance(result.ranking_data, pd.DataFrame)
    
    def test_get_top_exercises(self, sample_dataframe):
        """Test getting top exercises."""
        result = self.analyzer.get_top_exercises(sample_dataframe, top_n=2)
        
        assert isinstance(result, list)
        assert len(result) == 2
        
        for exercise in result:
            assert isinstance(exercise, ExerciseRanking)
            assert hasattr(exercise, 'rank')
            assert hasattr(exercise, 'exercise_name')
            assert hasattr(exercise, 'frequency')
            assert hasattr(exercise, 'percentage')
        
        # Check that exercises are ranked correctly
        assert result[0].rank == 1
        assert result[0].frequency == 3  # Bench Press
        assert result[1].rank == 2
        assert result[1].frequency == 2  # Squat
    
    def test_get_exercise_rank(self, sample_dataframe):
        """Test getting rank of specific exercise."""
        rank = self.analyzer.get_exercise_rank(sample_dataframe, 'Bench Press')
        assert rank == 1
        
        rank = self.analyzer.get_exercise_rank(sample_dataframe, 'Squat')
        assert rank == 2
        
        rank = self.analyzer.get_exercise_rank(sample_dataframe, 'Deadlift')
        assert rank == 3
        
        # Test case insensitive
        rank = self.analyzer.get_exercise_rank(sample_dataframe, 'bench press')
        assert rank == 1
        
        # Test non-existent exercise
        rank = self.analyzer.get_exercise_rank(sample_dataframe, 'Non-existent')
        assert rank is None
    
    def test_get_frequency_distribution(self, sample_dataframe):
        """Test frequency distribution calculation."""
        result = self.analyzer.get_frequency_distribution(sample_dataframe)
        
        assert isinstance(result, dict)
        assert '1-5 times' in result
        assert '6-10 times' in result
        assert '11-20 times' in result
        assert '21+ times' in result
        
        # Check that all exercises are accounted for
        total_exercises = sum(result.values())
        assert total_exercises == 3
    
    @patch('src.backend.all_exercise_statistics.filter_dataframe_by_timeframe')
    def test_analyze_by_timeframe(self, mock_filter, sample_dataframe):
        """Test timeframe analysis."""
        # Mock the filter to return filtered data
        filtered_df = sample_dataframe.iloc[:3]
        mock_filter.return_value = filtered_df
        
        result = self.analyzer.analyze_by_timeframe(sample_dataframe, 'Last 7 days')
        
        # Verify filter was called
        mock_filter.assert_called_once_with(sample_dataframe, 'Last 7 days')
        
        # Verify result
        assert isinstance(result, pd.DataFrame)
        assert 'exercise_name' in result.columns
        assert 'frequency' in result.columns


class TestTimeframeFiltering:
    """Test timeframe filtering functionality."""
    
    def test_filter_dataframe_by_timeframe_last_7_days(self, sample_workout_data_with_dates):
        """Test filtering for last 7 days."""
        result = filter_dataframe_by_timeframe(sample_workout_data_with_dates, 'Last 7 days')
        
        # Should only include workouts from last 7 days
        assert len(result) == 3  # First 3 workouts are within 7 days
        assert all(result['Workout Date'] >= datetime.now() - timedelta(days=7))
    
    def test_filter_dataframe_by_timeframe_last_30_days(self, sample_workout_data_with_dates):
        """Test filtering for last 30 days."""
        result = filter_dataframe_by_timeframe(sample_workout_data_with_dates, 'Last 30 days')
        
        # Should include all workouts (all within 30 days)
        assert len(result) == 4
        assert all(result['Workout Date'] >= datetime.now() - timedelta(days=30))
    
    def test_filter_dataframe_by_timeframe_all_time(self, sample_workout_data_with_dates):
        """Test filtering for all time (no filtering)."""
        result = filter_dataframe_by_timeframe(sample_workout_data_with_dates, 'All time')
        
        # Should return all data unchanged
        assert len(result) == 4
        assert result.equals(sample_workout_data_with_dates)
    
    def test_filter_dataframe_by_timeframe_invalid_timeframe(self, sample_workout_data_with_dates):
        """Test filtering with invalid timeframe."""
        result = filter_dataframe_by_timeframe(sample_workout_data_with_dates, 'Invalid Timeframe')
        
        # Should return all data unchanged
        assert len(result) == 4
        assert result.equals(sample_workout_data_with_dates)


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_analyze_all_exercises_single_exercise(self, sample_single_exercise_data):
        """Test with only one exercise type."""
        result = analyze_all_exercises(sample_single_exercise_data, 'Count')
        
        assert len(result) == 1
        assert result.iloc[0]['exercise_name'] == 'Bench Press'
        assert result.iloc[0]['count'] == 3
        assert result.iloc[0]['rank'] == 1
    
    def test_analyze_all_exercises_zero_values(self):
        """Test with zero values in numeric columns."""
        data = {
            'exercise_name': ['Bench Press', 'Squat'],
            'weight_lbs': [0, 0],
            'sets': [0, 0],
            'discrete_reps': [0, 0],
            'alternating': [False, False],
            'Workout Date': [
                datetime.now() - timedelta(days=1),
                datetime.now() - timedelta(days=2)
            ]
        }
        df = pd.DataFrame(data)
        
        result = analyze_all_exercises(df, 'Max Weight')
        
        assert len(result) == 2
        assert result.iloc[0]['max_weight'] == 0
        assert result.iloc[1]['max_weight'] == 0
    
    def test_analyze_all_exercises_missing_values(self, sample_invalid_data):
        """Test with missing values in DataFrame."""
        # Should handle missing values gracefully
        result = analyze_all_exercises(sample_invalid_data, 'Count')
        
        assert len(result) == 2  # Only non-null exercise names
        assert 'Bench Press' in result['exercise_name'].values
        assert 'Squat' in result['exercise_name'].values


class TestPerformance:
    """Performance tests for large datasets."""
    
    @pytest.mark.slow
    def test_analyze_all_exercises_large_dataset(self, large_workout_dataset):
        """Test performance with large dataset."""
        # Measure performance
        start_time = time.time()
        result = analyze_all_exercises(large_workout_dataset, 'Count')
        end_time = time.time()
        
        # Performance assertion (should complete within 5 seconds)
        assert end_time - start_time < 5.0
        
        # Verify result integrity
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 7  # Number of unique exercises in large_workout_dataset
        assert 'rank' in result.columns
        assert 'exercise_name' in result.columns
        assert 'count' in result.columns
    
    @pytest.mark.slow
    def test_workout_frequency_analyzer_large_dataset(self, large_workout_dataset):
        """Test WorkoutFrequencyAnalyzer performance with large dataset."""
        analyzer = WorkoutFrequencyAnalyzer()
        
        # Measure performance
        start_time = time.time()
        result = analyzer.analyze_exercise_frequency(large_workout_dataset)
        end_time = time.time()
        
        # Performance assertion (should complete within 3 seconds)
        assert end_time - start_time < 3.0
        
        # Verify result integrity
        assert isinstance(result, FrequencyAnalysisResult)
        assert result.total_exercises == 7  # Number of unique exercises in large_workout_dataset
        assert result.total_workouts == 1000  # Number of records in large_workout_dataset


class TestSecurity:
    """Security tests for input validation and data protection."""
    
    def test_analyze_all_exercises_sql_injection_attempt(self, sample_malicious_data):
        """Test protection against SQL injection attempts in exercise names."""
        # Should handle malicious input gracefully without executing code
        result = analyze_all_exercises(sample_malicious_data, 'Count')
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5
        # Verify that malicious strings are treated as regular exercise names
        assert all(name in result['exercise_name'].values for name in sample_malicious_data['exercise_name'])
    
    def test_analyze_all_exercises_xss_attempt(self, sample_malicious_data):
        """Test protection against XSS attempts in exercise names."""
        # Should handle malicious input gracefully
        result = analyze_all_exercises(sample_malicious_data, 'Count')
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5
        # Verify that malicious strings are treated as regular exercise names
        assert all(name in result['exercise_name'].values for name in sample_malicious_data['exercise_name'])
    
    def test_analyze_all_exercises_path_traversal_attempt(self, sample_malicious_data):
        """Test protection against path traversal attempts."""
        # Should handle malicious input gracefully
        result = analyze_all_exercises(sample_malicious_data, 'Count')
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5
        # Verify that malicious strings are treated as regular exercise names
        assert all(name in result['exercise_name'].values for name in sample_malicious_data['exercise_name'])
    
    def test_analyze_all_exercises_overflow_attempt(self, sample_edge_case_data):
        """Test protection against integer overflow attempts."""
        # Should handle large numbers gracefully
        result = analyze_all_exercises(sample_edge_case_data, 'Max Weight')
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5
        # Verify calculations work with large numbers
        assert result.iloc[0]['max_weight'] == 2**63 - 1
        assert result.iloc[1]['max_weight'] == 2**31 - 1


class TestDataValidation:
    """Data validation tests for input data quality."""
    
    def test_analyze_all_exercises_negative_values(self, sample_invalid_data):
        """Test handling of negative values in numeric columns."""
        # Should handle negative values gracefully
        result = analyze_all_exercises(sample_invalid_data, 'Max Weight')
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5
        # Verify negative values are processed correctly
        assert result.iloc[1]['max_weight'] == -185  # Second row has negative weight
    
    def test_analyze_all_exercises_extreme_values(self, sample_invalid_data):
        """Test handling of extreme values."""
        # Should handle extreme values gracefully
        result = analyze_all_exercises(sample_invalid_data, 'Max Weight')
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5
        # Verify extreme values are processed correctly
        assert result.iloc[3]['max_weight'] == float('inf')  # Fourth row has inf
        assert result.iloc[4]['max_weight'] == float('-inf')  # Fifth row has -inf
    
    def test_analyze_all_exercises_nan_values(self, sample_invalid_data):
        """Test handling of NaN values."""
        # Should handle NaN values gracefully
        result = analyze_all_exercises(sample_invalid_data, 'Count')
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5  # All exercises should still be counted
        assert 'Bench Press' in result['exercise_name'].values
        assert 'Squat' in result['exercise_name'].values


class TestStatisticalAccuracy:
    """Statistical accuracy tests for calculations."""
    
    def test_percentage_calculations_accuracy(self):
        """Test accuracy of percentage calculations."""
        data = {
            'exercise_name': ['A', 'B', 'C', 'A', 'B', 'A']
        }
        df = pd.DataFrame(data)
        
        result = calculate_percentage_breakdown(df)
        
        # Total frequency = 6
        # A: 3/6 = 50%
        # B: 2/6 = 33.33%
        # C: 1/6 = 16.67%
        assert abs(result['A'] - 50.0) < 0.01
        assert abs(result['B'] - 33.33) < 0.01
        assert abs(result['C'] - 16.67) < 0.01
        
        # Verify total adds up to 100%
        total_percentage = sum(result.values())
        assert abs(total_percentage - 100.0) < 0.01
    
    def test_average_calculations_accuracy(self):
        """Test accuracy of average calculations."""
        data = {
            'exercise_name': ['Bench Press', 'Bench Press', 'Bench Press'],
            'weight_lbs': [100, 200, 300],
            'sets': [3, 3, 3],
            'discrete_reps': [10, 10, 10],
            'alternating': [False, False, False],
            'Workout Date': [
                datetime.now() - timedelta(days=1),
                datetime.now() - timedelta(days=2),
                datetime.now() - timedelta(days=3)
            ]
        }
        df = pd.DataFrame(data)
        
        result = analyze_all_exercises(df, 'Average Reps')
        
        # Average reps should be 10.0
        assert result.iloc[0]['avg_reps'] == 10.0
    
    def test_volume_calculations_accuracy(self):
        """Test accuracy of volume calculations."""
        data = {
            'exercise_name': ['Bench Press', 'Bench Press'],
            'weight_lbs': [100, 200],
            'sets': [3, 3],
            'discrete_reps': [10, 10],
            'alternating': [False, False],
            'Workout Date': [
                datetime.now() - timedelta(days=1),
                datetime.now() - timedelta(days=2)
            ]
        }
        df = pd.DataFrame(data)
        
        result = analyze_all_exercises(df, 'Max Volume')
        
        # Volume calculations: 100*3*10 = 3000, 200*3*10 = 6000
        # Max volume should be 6000
        assert result.iloc[0]['max_volume'] == 6000


if __name__ == '__main__':
    pytest.main([__file__])

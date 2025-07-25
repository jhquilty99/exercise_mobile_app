"""
Test suite for all exercise statistics functionality.

Tests the analyze_all_exercises function and related functionality
as specified in BE-004: Exercise Frequency Analytics.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from ..all_exercise_statistics import (
    analyze_all_exercises,
    calculate_exercise_frequency,
    rank_exercises_by_frequency,
    calculate_percentage_breakdown,
    get_frequency_summary,
    WorkoutFrequencyAnalyzer,
    ExerciseRanking,
    FrequencyAnalysisResult
)
from ..filter import filter_dataframe_by_timeframe


class TestAnalyzeAllExercises:
    """Test the main analyze_all_exercises function."""
    
    @pytest.fixture
    def sample_dataframe(self):
        """Create a sample DataFrame for testing."""
        data = {
            'exercise_name': ['Bench Press', 'Squat', 'Deadlift', 'Bench Press', 'Squat', 'Bench Press'],
            'weight_lbs': [135, 185, 225, 145, 195, 155],
            'sets': [3, 3, 3, 3, 3, 3],
            'discrete_reps': [10, 8, 5, 12, 6, 11],
            'alternating': [False, False, False, False, False, False],
            'Workout Date': [
                datetime.now() - timedelta(days=1),
                datetime.now() - timedelta(days=2),
                datetime.now() - timedelta(days=3),
                datetime.now() - timedelta(days=4),
                datetime.now() - timedelta(days=5),
                datetime.now() - timedelta(days=6)
            ]
        }
        return pd.DataFrame(data)
    
    @pytest.fixture
    def sample_dataframe_alternating(self):
        """Create a sample DataFrame with alternating exercises."""
        data = {
            'exercise_name': ['Dumbbell Curl', 'Dumbbell Curl', 'Bench Press'],
            'weight_lbs': [25, 30, 135],
            'sets': [3, 3, 3],
            'discrete_reps': [12, 10, 10],
            'alternating': [True, True, False],
            'Workout Date': [
                datetime.now() - timedelta(days=1),
                datetime.now() - timedelta(days=2),
                datetime.now() - timedelta(days=3)
            ]
        }
        return pd.DataFrame(data)
    
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
    
    def test_analyze_all_exercises_max_volume_with_alternating(self, sample_dataframe_alternating):
        """Test max volume calculation with alternating exercises."""
        result = analyze_all_exercises(sample_dataframe_alternating, 'Max Volume')
        
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
    
    def test_analyze_all_exercises_empty_dataframe(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame(columns=['exercise_name', 'weight_lbs', 'sets', 'discrete_reps', 'alternating', 'Workout Date'])
        
        result = analyze_all_exercises(df, 'Count')
        
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
    
    @pytest.fixture
    def analyzer(self):
        """Create a WorkoutFrequencyAnalyzer instance."""
        return WorkoutFrequencyAnalyzer()
    
    @pytest.fixture
    def sample_dataframe(self):
        """Create a sample DataFrame for testing."""
        data = {
            'exercise_name': ['Bench Press', 'Squat', 'Deadlift', 'Bench Press', 'Squat', 'Bench Press'],
            'weight_lbs': [135, 185, 225, 145, 195, 155],
            'sets': [3, 3, 3, 3, 3, 3],
            'discrete_reps': [10, 8, 5, 12, 6, 11],
            'alternating': [False, False, False, False, False, False],
            'Workout Date': [
                datetime.now() - timedelta(days=1),
                datetime.now() - timedelta(days=2),
                datetime.now() - timedelta(days=3),
                datetime.now() - timedelta(days=4),
                datetime.now() - timedelta(days=5),
                datetime.now() - timedelta(days=6)
            ]
        }
        return pd.DataFrame(data)
    
    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initialization."""
        assert hasattr(analyzer, 'key_metrics')
        assert 'Max Volume' in analyzer.key_metrics
        assert 'Max Weight' in analyzer.key_metrics
        assert 'Average Reps' in analyzer.key_metrics
        assert 'Count' in analyzer.key_metrics
    
    def test_analyze_exercise_frequency(self, analyzer, sample_dataframe):
        """Test comprehensive frequency analysis."""
        result = analyzer.analyze_exercise_frequency(sample_dataframe)
        
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
    
    def test_get_top_exercises(self, analyzer, sample_dataframe):
        """Test getting top exercises."""
        result = analyzer.get_top_exercises(sample_dataframe, top_n=2)
        
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
    
    def test_get_exercise_rank(self, analyzer, sample_dataframe):
        """Test getting rank of specific exercise."""
        rank = analyzer.get_exercise_rank(sample_dataframe, 'Bench Press')
        assert rank == 1
        
        rank = analyzer.get_exercise_rank(sample_dataframe, 'Squat')
        assert rank == 2
        
        rank = analyzer.get_exercise_rank(sample_dataframe, 'Deadlift')
        assert rank == 3
        
        # Test case insensitive
        rank = analyzer.get_exercise_rank(sample_dataframe, 'bench press')
        assert rank == 1
        
        # Test non-existent exercise
        rank = analyzer.get_exercise_rank(sample_dataframe, 'Non-existent')
        assert rank is None
    
    def test_get_frequency_distribution(self, analyzer, sample_dataframe):
        """Test frequency distribution calculation."""
        result = analyzer.get_frequency_distribution(sample_dataframe)
        
        assert isinstance(result, dict)
        assert '1-5 times' in result
        assert '6-10 times' in result
        assert '11-20 times' in result
        assert '21+ times' in result
        
        # Check that all exercises are accounted for
        total_exercises = sum(result.values())
        assert total_exercises == 3
    
    @patch('src.backend.all_exercise_statistics.filter_dataframe_by_timeframe')
    def test_analyze_by_timeframe(self, mock_filter, analyzer, sample_dataframe):
        """Test timeframe analysis."""
        # Mock the filter to return filtered data
        filtered_df = sample_dataframe.iloc[:3]
        mock_filter.return_value = filtered_df
        
        result = analyzer.analyze_by_timeframe(sample_dataframe, 'Last 7 days')
        
        # Verify filter was called
        mock_filter.assert_called_once_with(sample_dataframe, 'Last 7 days')
        
        # Verify result
        assert isinstance(result, pd.DataFrame)
        assert 'exercise_name' in result.columns
        assert 'frequency' in result.columns


class TestTimeframeFiltering:
    """Test timeframe filtering functionality."""
    
    @pytest.fixture
    def sample_dataframe_with_dates(self):
        """Create a sample DataFrame with workout dates."""
        data = {
            'exercise_name': ['Bench Press', 'Squat', 'Deadlift', 'Bench Press'],
            'weight_lbs': [135, 185, 225, 145],
            'sets': [3, 3, 3, 3],
            'discrete_reps': [10, 8, 5, 12],
            'alternating': [False, False, False, False],
            'Workout Date': [
                datetime.now() - timedelta(days=1),  # Recent
                datetime.now() - timedelta(days=5),  # Recent
                datetime.now() - timedelta(days=10), # Recent
                datetime.now() - timedelta(days=20)  # Older
            ]
        }
        return pd.DataFrame(data)
    
    def test_filter_dataframe_by_timeframe_last_7_days(self, sample_dataframe_with_dates):
        """Test filtering for last 7 days."""
        result = filter_dataframe_by_timeframe(sample_dataframe_with_dates, 'Last 7 days')
        
        # Should only include workouts from last 7 days
        assert len(result) == 3  # First 3 workouts are within 7 days
        assert all(result['Workout Date'] >= datetime.now() - timedelta(days=7))
    
    def test_filter_dataframe_by_timeframe_last_30_days(self, sample_dataframe_with_dates):
        """Test filtering for last 30 days."""
        result = filter_dataframe_by_timeframe(sample_dataframe_with_dates, 'Last 30 days')
        
        # Should include all workouts (all within 30 days)
        assert len(result) == 4
        assert all(result['Workout Date'] >= datetime.now() - timedelta(days=30))
    
    def test_filter_dataframe_by_timeframe_all_time(self, sample_dataframe_with_dates):
        """Test filtering for all time (no filtering)."""
        result = filter_dataframe_by_timeframe(sample_dataframe_with_dates, 'All time')
        
        # Should return all data unchanged
        assert len(result) == 4
        assert result.equals(sample_dataframe_with_dates)
    
    def test_filter_dataframe_by_timeframe_invalid_timeframe(self, sample_dataframe_with_dates):
        """Test filtering with invalid timeframe."""
        result = filter_dataframe_by_timeframe(sample_dataframe_with_dates, 'Invalid Timeframe')
        
        # Should return all data unchanged
        assert len(result) == 4
        assert result.equals(sample_dataframe_with_dates)


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_analyze_all_exercises_single_exercise(self):
        """Test with only one exercise type."""
        data = {
            'exercise_name': ['Bench Press', 'Bench Press', 'Bench Press'],
            'weight_lbs': [135, 145, 155],
            'sets': [3, 3, 3],
            'discrete_reps': [10, 12, 11],
            'alternating': [False, False, False],
            'Workout Date': [
                datetime.now() - timedelta(days=1),
                datetime.now() - timedelta(days=2),
                datetime.now() - timedelta(days=3)
            ]
        }
        df = pd.DataFrame(data)
        
        result = analyze_all_exercises(df, 'Count')
        
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
    
    def test_analyze_all_exercises_missing_values(self):
        """Test with missing values in DataFrame."""
        data = {
            'exercise_name': ['Bench Press', 'Squat', None],
            'weight_lbs': [135, 185, None],
            'sets': [3, 3, None],
            'discrete_reps': [10, 8, None],
            'alternating': [False, False, None],
            'Workout Date': [
                datetime.now() - timedelta(days=1),
                datetime.now() - timedelta(days=2),
                None
            ]
        }
        df = pd.DataFrame(data)
        
        # Should handle missing values gracefully
        result = analyze_all_exercises(df, 'Count')
        
        assert len(result) == 2  # Only non-null exercise names
        assert 'Bench Press' in result['exercise_name'].values
        assert 'Squat' in result['exercise_name'].values


if __name__ == '__main__':
    pytest.main([__file__])

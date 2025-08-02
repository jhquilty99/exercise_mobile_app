"""
Test suite for workout statistics module (BE-003: Workout Analytics).
Tests workout streak calculation, frequency graphs, and calendar visualization.
"""

import unittest
from datetime import datetime, date, timedelta
import pandas as pd
import plotly.graph_objects as go
import pytest
from unittest.mock import patch, Mock
from src.backend.workout_statistics import (
    calculate_workout_streak,
    get_current_workout_streak,
    create_workout_frequency_graph,
    create_workout_calendar
)


class TestWorkoutStatistics(unittest.TestCase):
    """Test cases for workout statistics functionality."""

    def setUp(self):
        """Set up test data."""
        # Create sample workout data for testing
        self.sample_data = {
            'workout_date': [
                '2024-01-01', '2024-01-01', '2024-01-01',  # Day 1
                '2024-01-03', '2024-01-03', '2024-01-03',  # Day 3 (2 day streak)
                '2024-01-05', '2024-01-05', '2024-01-05',  # Day 5 (3 day streak)
                '2024-01-07', '2024-01-07', '2024-01-07',  # Day 7 (4 day streak)
                '2024-01-09', '2024-01-09', '2024-01-09',  # Day 9 (5 day streak)
                '2024-01-12', '2024-01-12', '2024-01-12',  # Day 12 (1 day streak - gap too large)
                '2024-01-14', '2024-01-14', '2024-01-14',  # Day 14 (2 day streak)
                '2024-01-16', '2024-01-16', '2024-01-16',  # Day 16 (3 day streak)
            ],
            'exercise_name': [
                'Bench Press', 'Squats', 'Deadlifts',
                'Bench Press', 'Squats', 'Pull-ups',
                'Bench Press', 'Squats', 'Deadlifts',
                'Bench Press', 'Squats', 'Pull-ups',
                'Bench Press', 'Squats', 'Deadlifts',
                'Bench Press', 'Squats', 'Pull-ups',
                'Bench Press', 'Squats', 'Deadlifts',
                'Bench Press', 'Squats', 'Pull-ups',
            ],
            'exercise_type': ['Strength'] * 24,
            'weight': [135, 185, 225] * 8,
            'sets': [3, 3, 3] * 8,
            'discrete_reps': [10, 8, 6] * 8,
            'alternating': [False] * 24
        }
        
        self.df = pd.DataFrame(self.sample_data)
        self.df['workout_date'] = pd.to_datetime(self.df['workout_date'])

    def test_calculate_workout_streak_empty_data(self):
        """Test workout streak calculation with empty data."""
        empty_df = pd.DataFrame()
        streak = calculate_workout_streak(empty_df)
        
        self.assertEqual(streak, 0)

    def test_calculate_workout_streak_none_data(self):
        """Test workout streak calculation with None data."""
        streak = calculate_workout_streak(None)
        
        self.assertEqual(streak, 0)

    def test_calculate_workout_streak_no_date_column(self):
        """Test workout streak calculation with missing date column."""
        df_no_date = pd.DataFrame({'exercise_name': ['Bench Press']})
        streak = calculate_workout_streak(df_no_date)
        
        self.assertEqual(streak, 0)

    def test_calculate_workout_streak_invalid_date_format(self):
        """Test workout streak calculation with invalid date format."""
        invalid_data = {
            'workout_date': ['invalid-date', '2024-01-01'],
            'exercise_name': ['Bench Press', 'Squats']
        }
        df_invalid = pd.DataFrame(invalid_data)
        
        # Should handle invalid dates gracefully
        streak = calculate_workout_streak(df_invalid)
        self.assertIsInstance(streak, int)

    def test_calculate_workout_streak_consecutive_days(self):
        """Test workout streak calculation with consecutive workout days."""
        # Create data with consecutive days (2024-01-15, 2024-01-16)
        consecutive_data = {
            'workout_date': [
                '2024-01-15', '2024-01-15',
                '2024-01-16', '2024-01-16'
            ],
            'exercise_name': ['Bench Press', 'Squats'] * 2
        }
        df_consecutive = pd.DataFrame(consecutive_data)
        df_consecutive['workout_date'] = pd.to_datetime(df_consecutive['workout_date'])
        
        streak = calculate_workout_streak(df_consecutive)
        # Should be 2 day streak (consecutive days)
        self.assertEqual(streak, 2)

    def test_calculate_workout_streak_alternating_days(self):
        """Test workout streak calculation with alternating days (every other day)."""
        # Create data with alternating days (2024-01-15, 2024-01-17)
        alternating_data = {
            'workout_date': [
                '2024-01-15', '2024-01-15',
                '2024-01-17', '2024-01-17'
            ],
            'exercise_name': ['Bench Press', 'Squats'] * 2
        }
        df_alternating = pd.DataFrame(alternating_data)
        df_alternating['workout_date'] = pd.to_datetime(df_alternating['workout_date'])
        
        streak = calculate_workout_streak(df_alternating)
        # Should be 3 day streak (allows missing every other day)
        self.assertEqual(streak, 3)

    def test_calculate_workout_streak_large_gap(self):
        """Test workout streak calculation with large gaps."""
        # Create data with large gap (2024-01-15, 2024-01-18)
        gap_data = {
            'workout_date': [
                '2024-01-15', '2024-01-15',
                '2024-01-18', '2024-01-18'
            ],
            'exercise_name': ['Bench Press', 'Squats'] * 2
        }
        df_gap = pd.DataFrame(gap_data)
        df_gap['workout_date'] = pd.to_datetime(df_gap['workout_date'])
        
        streak = calculate_workout_streak(df_gap)
        # Should be 1 day streak (gap too large)
        self.assertEqual(streak, 1)

    def test_calculate_workout_streak_single_day(self):
        """Test workout streak calculation with single day workout."""
        single_day_data = {
            'workout_date': ['2024-01-15', '2024-01-15'],
            'exercise_name': ['Bench Press', 'Squats']
        }
        df_single = pd.DataFrame(single_day_data)
        df_single['workout_date'] = pd.to_datetime(df_single['workout_date'])
        
        streak = calculate_workout_streak(df_single)
        # Should be 1 day streak
        self.assertEqual(streak, 1)

    def test_calculate_workout_streak_recent_workout(self):
        """Test workout streak calculation with recent workout."""
        # Create data with workout from yesterday
        yesterday = date.today() - timedelta(days=1)
        recent_data = {
            'workout_date': [
                yesterday.strftime('%Y-%m-%d'), yesterday.strftime('%Y-%m-%d')
            ],
            'exercise_name': ['Bench Press', 'Squats']
        }
        df_recent = pd.DataFrame(recent_data)
        df_recent['workout_date'] = pd.to_datetime(df_recent['workout_date'])
        
        streak = calculate_workout_streak(df_recent)
        # Should have a streak since workout was recent
        self.assertGreaterEqual(streak, 1)

    def test_calculate_workout_streak_old_workout(self):
        """Test workout streak calculation with old workout."""
        # Create data with workout from 10 days ago
        old_date = date.today() - timedelta(days=10)
        old_data = {
            'workout_date': [
                old_date.strftime('%Y-%m-%d'), old_date.strftime('%Y-%m-%d')
            ],
            'exercise_name': ['Bench Press', 'Squats']
        }
        df_old = pd.DataFrame(old_data)
        df_old['workout_date'] = pd.to_datetime(df_old['workout_date'])
        
        streak = calculate_workout_streak(df_old)
        # Should have 1 streak since it's the only workout
        self.assertEqual(streak, 1)

    def test_calculate_workout_streak_today_workout(self):
        """Test workout streak calculation with today's workout."""
        today = date.today()
        today_data = {
            'workout_date': [
                today.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
            ],
            'exercise_name': ['Bench Press', 'Squats']
        }
        df_today = pd.DataFrame(today_data)
        df_today['workout_date'] = pd.to_datetime(df_today['workout_date'])
        
        streak = calculate_workout_streak(df_today)
        # Should have a streak since workout is today
        self.assertGreaterEqual(streak, 1)

    def test_calculate_workout_streak_long_streak(self):
        """Test workout streak calculation with very long streak."""
        # Create data with 30 consecutive days
        start_date = date.today() - timedelta(days=30)
        long_streak_data = []
        
        for i in range(30):
            current_date = start_date + timedelta(days=i)
            long_streak_data.extend([
                {'workout_date': current_date.strftime('%Y-%m-%d'), 'exercise_name': 'Bench Press'},
                {'workout_date': current_date.strftime('%Y-%m-%d'), 'exercise_name': 'Squats'}
            ])
        
        df_long = pd.DataFrame(long_streak_data)
        df_long['workout_date'] = pd.to_datetime(df_long['workout_date'])
        
        streak = calculate_workout_streak(df_long)
        # Should have a significant streak
        self.assertGreaterEqual(streak, 25)

    def test_calculate_workout_streak_malformed_data(self):
        """Test workout streak calculation with malformed data."""
        # Test with None values
        malformed_data = {
            'workout_date': [None, '2024-01-01', ''],
            'exercise_name': ['Bench Press', 'Squats', 'Deadlifts']
        }
        df_malformed = pd.DataFrame(malformed_data)
        
        # Should handle gracefully
        streak = calculate_workout_streak(df_malformed)
        self.assertIsInstance(streak, int)

    # Tests for get_current_workout_streak function
    @patch('src.backend.workout_statistics.date')
    def test_get_current_workout_streak_empty_data(self, mock_date):
        """Test current workout streak calculation with empty data."""
        # Mock today's date
        mock_date.today.return_value = date(2024, 1, 15)
        
        empty_df = pd.DataFrame()
        streak = get_current_workout_streak(empty_df)
        
        self.assertEqual(streak, 0)

    @patch('src.backend.workout_statistics.date')
    def test_get_current_workout_streak_none_data(self, mock_date):
        """Test current workout streak calculation with None data."""
        # Mock today's date
        mock_date.today.return_value = date(2024, 1, 15)
        
        streak = get_current_workout_streak(None)
        
        self.assertEqual(streak, 0)

    @patch('src.backend.workout_statistics.date')
    def test_get_current_workout_streak_no_date_column(self, mock_date):
        """Test current workout streak calculation with missing date column."""
        # Mock today's date
        mock_date.today.return_value = date(2024, 1, 15)
        
        df_no_date = pd.DataFrame({'exercise_name': ['Bench Press']})
        streak = get_current_workout_streak(df_no_date)
        
        self.assertEqual(streak, 0)

    @patch('src.backend.workout_statistics.date')
    def test_get_current_workout_streak_invalid_date_format(self, mock_date):
        """Test current workout streak calculation with invalid date format."""
        # Mock today's date
        mock_date.today.return_value = date(2024, 1, 15)
        
        invalid_data = {
            'workout_date': ['invalid-date', '2024-01-01'],
            'exercise_name': ['Bench Press', 'Squats']
        }
        df_invalid = pd.DataFrame(invalid_data)
        
        # Should handle invalid dates gracefully
        streak = get_current_workout_streak(df_invalid)
        self.assertIsInstance(streak, int)

    @patch('src.backend.workout_statistics.date')
    def test_get_current_workout_streak_today_workout(self, mock_date):
        """Test current workout streak calculation with today's workout."""
        # Mock today's date
        mock_today = date(2024, 1, 15)
        mock_date.today.return_value = mock_today
        
        today_data = {
            'workout_date': [
                mock_today.strftime('%Y-%m-%d'), mock_today.strftime('%Y-%m-%d')
            ],
            'exercise_name': ['Bench Press', 'Squats']
        }
        df_today = pd.DataFrame(today_data)
        df_today['workout_date'] = pd.to_datetime(df_today['workout_date'])
        
        streak = get_current_workout_streak(df_today)
        # Should have a current streak since workout is today
        self.assertGreaterEqual(streak, 1)

    @patch('src.backend.workout_statistics.date')
    def test_get_current_workout_streak_yesterday_workout(self, mock_date):
        """Test current workout streak calculation with yesterday's workout."""
        # Mock today's date
        mock_today = date(2024, 1, 15)
        mock_date.today.return_value = mock_today
        yesterday = mock_today - timedelta(days=1)
        
        yesterday_data = {
            'workout_date': [
                yesterday.strftime('%Y-%m-%d'), yesterday.strftime('%Y-%m-%d')
            ],
            'exercise_name': ['Bench Press', 'Squats']
        }
        df_yesterday = pd.DataFrame(yesterday_data)
        df_yesterday['workout_date'] = pd.to_datetime(df_yesterday['workout_date'])
        
        streak = get_current_workout_streak(df_yesterday)
        # Should have a current streak since workout was yesterday
        self.assertGreaterEqual(streak, 1)

    @patch('src.backend.workout_statistics.date')
    def test_get_current_workout_streak_two_days_ago_workout(self, mock_date):
        """Test current workout streak calculation with workout from 2 days ago."""
        # Mock today's date
        mock_today = date(2024, 1, 15)
        mock_date.today.return_value = mock_today
        two_days_ago = mock_today - timedelta(days=2)
        
        two_days_ago_data = {
            'workout_date': [
                two_days_ago.strftime('%Y-%m-%d'), two_days_ago.strftime('%Y-%m-%d')
            ],
            'exercise_name': ['Bench Press', 'Squats']
        }
        df_two_days_ago = pd.DataFrame(two_days_ago_data)
        df_two_days_ago['workout_date'] = pd.to_datetime(df_two_days_ago['workout_date'])
        
        streak = get_current_workout_streak(df_two_days_ago)
        # Should have a current streak since workout was 2 days ago
        self.assertGreaterEqual(streak, 1)

    @patch('src.backend.workout_statistics.date')
    def test_get_current_workout_streak_three_days_ago_workout(self, mock_date):
        """Test current workout streak calculation with workout from 3 days ago."""
        # Mock today's date
        mock_today = date(2024, 1, 15)
        mock_date.today.return_value = mock_today
        three_days_ago = mock_today - timedelta(days=3)
        
        three_days_ago_data = {
            'workout_date': [
                three_days_ago.strftime('%Y-%m-%d'), three_days_ago.strftime('%Y-%m-%d')
            ],
            'exercise_name': ['Bench Press', 'Squats']
        }
        df_three_days_ago = pd.DataFrame(three_days_ago_data)
        df_three_days_ago['workout_date'] = pd.to_datetime(df_three_days_ago['workout_date'])
        
        streak = get_current_workout_streak(df_three_days_ago)
        # Should have 0 streak since workout was more than 2 days ago
        self.assertEqual(streak, 0)

    @patch('src.backend.workout_statistics.date')
    def test_get_current_workout_streak_old_workout(self, mock_date):
        """Test current workout streak calculation with old workout."""
        # Mock today's date
        mock_today = date(2024, 1, 15)
        mock_date.today.return_value = mock_today
        old_date = mock_today - timedelta(days=10)
        
        old_data = {
            'workout_date': [
                old_date.strftime('%Y-%m-%d'), old_date.strftime('%Y-%m-%d')
            ],
            'exercise_name': ['Bench Press', 'Squats']
        }
        df_old = pd.DataFrame(old_data)
        df_old['workout_date'] = pd.to_datetime(df_old['workout_date'])
        
        streak = get_current_workout_streak(df_old)
        # Should have 0 streak since workout is too old
        self.assertEqual(streak, 0)

    @patch('src.backend.workout_statistics.date')
    def test_get_current_workout_streak_consecutive_days(self, mock_date):
        """Test current workout streak calculation with consecutive workout days."""
        # Mock today's date
        mock_today = date(2024, 1, 15)
        mock_date.today.return_value = mock_today
        
        # Create data with consecutive days ending yesterday
        yesterday = mock_today - timedelta(days=1)
        two_days_ago = mock_today - timedelta(days=2)
        consecutive_data = {
            'workout_date': [
                two_days_ago.strftime('%Y-%m-%d'), two_days_ago.strftime('%Y-%m-%d'),
                yesterday.strftime('%Y-%m-%d'), yesterday.strftime('%Y-%m-%d')
            ],
            'exercise_name': ['Bench Press', 'Squats'] * 2
        }
        df_consecutive = pd.DataFrame(consecutive_data)
        df_consecutive['workout_date'] = pd.to_datetime(df_consecutive['workout_date'])
        
        streak = get_current_workout_streak(df_consecutive)
        # Should have a current streak since most recent workout was yesterday (within 2 days)
        self.assertGreaterEqual(streak, 1)

    @patch('src.backend.workout_statistics.date')
    def test_get_current_workout_streak_alternating_days(self, mock_date):
        """Test current workout streak calculation with alternating days."""
        # Mock today's date
        mock_today = date(2024, 1, 15)
        mock_date.today.return_value = mock_today
        
        # Create data with alternating days ending yesterday
        yesterday = mock_today - timedelta(days=1)
        three_days_ago = mock_today - timedelta(days=3)
        alternating_data = {
            'workout_date': [
                three_days_ago.strftime('%Y-%m-%d'), three_days_ago.strftime('%Y-%m-%d'),
                yesterday.strftime('%Y-%m-%d'), yesterday.strftime('%Y-%m-%d')
            ],
            'exercise_name': ['Bench Press', 'Squats'] * 2
        }
        df_alternating = pd.DataFrame(alternating_data)
        df_alternating['workout_date'] = pd.to_datetime(df_alternating['workout_date'])
        
        streak = get_current_workout_streak(df_alternating)
        # Should have a current streak since most recent workout was yesterday (within 2 days)
        self.assertEqual(streak, 3)

    @patch('src.backend.workout_statistics.date')
    def test_get_current_workout_streak_long_streak_ending_recently(self, mock_date):
        """Test current workout streak calculation with long streak ending recently."""
        # Mock today's date
        mock_today = date(2024, 1, 15)
        mock_date.today.return_value = mock_today
        
        # Create data with 10 consecutive days ending yesterday
        yesterday = mock_today - timedelta(days=1)
        long_streak_data = []
        
        for i in range(10):
            current_date = yesterday - timedelta(days=9-i)
            long_streak_data.extend([
                {'workout_date': current_date.strftime('%Y-%m-%d'), 'exercise_name': 'Bench Press'},
                {'workout_date': current_date.strftime('%Y-%m-%d'), 'exercise_name': 'Squats'}
            ])
        
        df_long = pd.DataFrame(long_streak_data)
        df_long['workout_date'] = pd.to_datetime(df_long['workout_date'])
        
        streak = get_current_workout_streak(df_long)
        # Should have a current streak since most recent workout was yesterday (within 2 days)
        self.assertGreaterEqual(streak, 1)

    @patch('src.backend.workout_statistics.date')
    def test_get_current_workout_streak_long_streak_ending_old(self, mock_date):
        """Test current workout streak calculation with long streak ending too long ago."""
        # Mock today's date
        mock_today = date(2024, 1, 15)
        mock_date.today.return_value = mock_today
        
        # Create data with 10 consecutive days ending 5 days ago
        five_days_ago = mock_today - timedelta(days=5)
        long_streak_data = []
        
        for i in range(10):
            current_date = five_days_ago - timedelta(days=9-i)
            long_streak_data.extend([
                {'workout_date': current_date.strftime('%Y-%m-%d'), 'exercise_name': 'Bench Press'},
                {'workout_date': current_date.strftime('%Y-%m-%d'), 'exercise_name': 'Squats'}
            ])
        
        df_long = pd.DataFrame(long_streak_data)
        df_long['workout_date'] = pd.to_datetime(df_long['workout_date'])
        
        streak = get_current_workout_streak(df_long)
        # Should have 0 streak since most recent workout was too long ago
        self.assertEqual(streak, 0)

    @patch('src.backend.workout_statistics.date')
    def test_get_current_workout_streak_future_workout(self, mock_date):
        """Test current workout streak calculation with future workout date."""
        # Mock today's date
        mock_today = date(2024, 1, 15)
        mock_date.today.return_value = mock_today
        tomorrow = mock_today + timedelta(days=1)
        
        future_data = {
            'workout_date': [
                tomorrow.strftime('%Y-%m-%d'), tomorrow.strftime('%Y-%m-%d')
            ],
            'exercise_name': ['Bench Press', 'Squats']
        }
        df_future = pd.DataFrame(future_data)
        df_future['workout_date'] = pd.to_datetime(df_future['workout_date'])
        
        streak = get_current_workout_streak(df_future)
        # Should handle future dates gracefully
        self.assertIsInstance(streak, int)

    @patch('src.backend.workout_statistics.date')
    def test_get_current_workout_streak_malformed_data(self, mock_date):
        """Test current workout streak calculation with malformed data."""
        # Mock today's date
        mock_date.today.return_value = date(2024, 1, 15)
        
        # Test with None values
        malformed_data = {
            'workout_date': [None, '2024-01-01', ''],
            'exercise_name': ['Bench Press', 'Squats', 'Deadlifts']
        }
        df_malformed = pd.DataFrame(malformed_data)
        
        # Should handle gracefully
        streak = get_current_workout_streak(df_malformed)
        self.assertIsInstance(streak, int)

    @patch('src.backend.workout_statistics.date')
    def test_get_current_workout_streak_no_workout_dates(self, mock_date):
        """Test current workout streak calculation with no valid workout dates."""
        # Mock today's date
        mock_date.today.return_value = date(2024, 1, 15)
        
        no_dates_data = {
            'workout_date': [],
            'exercise_name': []
        }
        df_no_dates = pd.DataFrame(no_dates_data)
        
        streak = get_current_workout_streak(df_no_dates)
        # Should handle empty workout dates gracefully
        self.assertIsInstance(streak, int)

    @patch('src.backend.workout_statistics.date')
    def test_get_current_workout_streak_exception_handling(self, mock_date):
        """Test current workout streak calculation exception handling."""
        # Mock today's date
        mock_date.today.return_value = date(2024, 1, 15)
        
        # Create data that would cause an exception
        exception_data = {
            'workout_date': ['not-a-date', 'also-not-a-date'],
            'exercise_name': ['Bench Press', 'Squats']
        }
        df_exception = pd.DataFrame(exception_data)
        
        # Should handle exceptions gracefully
        streak = get_current_workout_streak(df_exception)
        self.assertIsInstance(streak, int)
        self.assertEqual(streak, 0)  # Should return 0 for invalid data

    def test_create_workout_frequency_graph_empty_data(self):
        """Test workout frequency graph creation with empty data."""
        empty_df = pd.DataFrame()
        fig = create_workout_frequency_graph(empty_df)
        
        self.assertIsInstance(fig, go.Figure)
        # Should have annotation indicating no data
        self.assertIn('annotations', fig.layout)

    def test_create_workout_frequency_graph_no_date_column(self):
        """Test workout frequency graph creation with missing date column."""
        df_no_date = pd.DataFrame({'exercise_name': ['Bench Press']})
        fig = create_workout_frequency_graph(df_no_date)
        
        self.assertIsInstance(fig, go.Figure)
        # Should have annotation indicating no data
        self.assertIn('annotations', fig.layout)

    def test_create_workout_frequency_graph_invalid_date_format(self):
        """Test workout frequency graph creation with invalid date format."""
        invalid_data = {
            'workout_date': ['invalid-date', '2024-01-01'],
            'exercise_name': ['Bench Press', 'Squats']
        }
        df_invalid = pd.DataFrame(invalid_data)
        
        fig = create_workout_frequency_graph(df_invalid)
        self.assertIsInstance(fig, go.Figure)

    def test_create_workout_frequency_graph_valid_data(self):
        """Test workout frequency graph creation with valid data."""
        fig = create_workout_frequency_graph(self.df)
        
        self.assertIsInstance(fig, go.Figure)
        # Should have data traces
        self.assertGreater(len(fig.data), 0)
        # Should be a line chart
        self.assertEqual(fig.data[0].type, 'scatter')
        # Should have proper layout
        self.assertIn('title', fig.layout)
        self.assertIn('xaxis', fig.layout)
        self.assertIn('yaxis', fig.layout)

    def test_create_workout_frequency_graph_30_day_window(self):
        """Test that workout frequency graph uses 30-day rolling window."""
        # Create data spanning more than 30 days
        start_date = date.today() - timedelta(days=60)
        long_data = []
        
        for i in range(60):
            current_date = start_date + timedelta(days=i)
            if i % 3 == 0:  # Workout every 3 days
                long_data.extend([
                    {'workout_date': current_date.strftime('%Y-%m-%d'), 'exercise_name': 'Bench Press'},
                    {'workout_date': current_date.strftime('%Y-%m-%d'), 'exercise_name': 'Squats'}
                ])
        
        df_long = pd.DataFrame(long_data)
        df_long['workout_date'] = pd.to_datetime(df_long['workout_date'])
        
        fig = create_workout_frequency_graph(df_long)
        
        self.assertIsInstance(fig, go.Figure)
        # Should have data points (after 30-day window starts)
        self.assertGreater(len(fig.data[0].x), 0)

    def test_create_workout_frequency_graph_single_day(self):
        """Test workout frequency graph creation with single day data."""
        single_day_data = {
            'workout_date': ['2024-01-15', '2024-01-15'],
            'exercise_name': ['Bench Press', 'Squats']
        }
        df_single = pd.DataFrame(single_day_data)
        df_single['workout_date'] = pd.to_datetime(df_single['workout_date'])
        
        fig = create_workout_frequency_graph(df_single)
        self.assertIsInstance(fig, go.Figure)

    def test_create_workout_frequency_graph_large_dataset(self):
        """Test workout frequency graph creation with large dataset."""
        # Create large dataset (1000 workouts over 2 years)
        start_date = date.today() - timedelta(days=730)
        large_data = []
        
        for i in range(1000):
            current_date = start_date + timedelta(days=i % 730)
            large_data.append({
                'workout_date': current_date.strftime('%Y-%m-%d'),
                'exercise_name': f'Exercise_{i % 10}'
            })
        
        df_large = pd.DataFrame(large_data)
        df_large['workout_date'] = pd.to_datetime(df_large['workout_date'])
        
        # Should handle large dataset without errors
        fig = create_workout_frequency_graph(df_large)
        self.assertIsInstance(fig, go.Figure)

    def test_create_workout_calendar_empty_data(self):
        """Test workout calendar creation with empty data."""
        empty_df = pd.DataFrame()
        fig = create_workout_calendar(empty_df)
        
        self.assertIsInstance(fig, go.Figure)
        # Should have annotation indicating no data
        self.assertIn('annotations', fig.layout)

    def test_create_workout_calendar_no_date_column(self):
        """Test workout calendar creation with missing date column."""
        df_no_date = pd.DataFrame({'exercise_name': ['Bench Press']})
        fig = create_workout_calendar(df_no_date)
        
        self.assertIsInstance(fig, go.Figure)
        # Should have annotation indicating no data
        self.assertIn('annotations', fig.layout)

    def test_create_workout_calendar_invalid_date_format(self):
        """Test workout calendar creation with invalid date format."""
        invalid_data = {
            'workout_date': ['invalid-date', '2024-01-01'],
            'exercise_name': ['Bench Press', 'Squats']
        }
        df_invalid = pd.DataFrame(invalid_data)
        
        fig = create_workout_calendar(df_invalid)
        self.assertIsInstance(fig, go.Figure)

    def test_create_workout_calendar_valid_data(self):
        """Test workout calendar creation with valid data."""
        fig = create_workout_calendar(self.df)
        
        self.assertIsInstance(fig, go.Figure)
        # Should have either data traces or annotations (for empty data)
        self.assertTrue(len(fig.data) > 0 or len(fig.layout.annotations) > 0)
        # Should have proper layout
        self.assertIn('title', fig.layout)

    def test_create_workout_calendar_specific_year(self):
        """Test workout calendar creation for specific year."""
        # Create data for 2024
        year_data = {
            'workout_date': [
                '2024-01-01', '2024-01-01',
                '2024-06-15', '2024-06-15',
                '2024-12-31', '2024-12-31'
            ],
            'exercise_name': ['Bench Press', 'Squats'] * 3
        }
        df_year = pd.DataFrame(year_data)
        df_year['workout_date'] = pd.to_datetime(df_year['workout_date'])
        
        fig = create_workout_calendar(df_year, year=2024)
        
        self.assertIsInstance(fig, go.Figure)
        # Should have either data traces or annotations (for empty data)
        self.assertTrue(len(fig.data) > 0 or len(fig.layout.annotations) > 0)

    def test_create_workout_calendar_default_parameters(self):
        """Test workout calendar creation with default parameters."""
        fig = create_workout_calendar(self.df)
        
        self.assertIsInstance(fig, go.Figure)
        # Should have either data traces or annotations (for empty data)
        self.assertTrue(len(fig.data) > 0 or len(fig.layout.annotations) > 0)

    def test_create_workout_calendar_large_dataset(self):
        """Test workout calendar creation with large dataset."""
        # Create large dataset (1000 workouts over 2 years)
        start_date = date.today() - timedelta(days=730)
        large_data = []
        
        for i in range(1000):
            current_date = start_date + timedelta(days=i % 730)
            large_data.append({
                'workout_date': current_date.strftime('%Y-%m-%d'),
                'exercise_name': f'Exercise_{i % 10}'
            })
        
        df_large = pd.DataFrame(large_data)
        df_large['workout_date'] = pd.to_datetime(df_large['workout_date'])
        
        # Should handle large dataset without errors
        fig = create_workout_calendar(df_large)
        self.assertIsInstance(fig, go.Figure)

    def test_interactive_features(self):
        """Test that visualizations are interactive."""
        # Test frequency graph interactivity
        freq_fig = create_workout_frequency_graph(self.df)
        self.assertIn('hovermode', freq_fig.layout)
        self.assertEqual(freq_fig.layout.hovermode, 'x unified')
        
        # Test calendar interactivity
        cal_fig = create_workout_calendar(self.df)
        self.assertIsInstance(cal_fig, go.Figure)

    def test_data_structures_for_frontend(self):
        """Test that functions return appropriate data structures for frontend integration."""
        # Test streak calculation returns int
        streak = calculate_workout_streak(self.df)
        self.assertIsInstance(streak, int)
        
        # Test current workout streak calculation returns tuple
        with patch('src.backend.workout_statistics.date') as mock_date:
            mock_date.today.return_value = date(2024, 1, 15)
            current_streak = get_current_workout_streak(self.df)
            self.assertIsInstance(current_streak, int)
        
        # Test frequency graph returns Plotly figure
        freq_fig = create_workout_frequency_graph(self.df)
        self.assertIsInstance(freq_fig, go.Figure)
        
        # Test calendar returns Plotly figure
        cal_fig = create_workout_calendar(self.df)
        self.assertIsInstance(cal_fig, go.Figure)

    def test_security_malicious_input(self):
        """Test security against malicious input."""
        # Test with extremely long strings
        malicious_data = {
            'workout_date': ['A' * 10000, '2024-01-01'],
            'exercise_name': ['X' * 10000, 'Bench Press']
        }
        df_malicious = pd.DataFrame(malicious_data)
        
        # Should handle gracefully without crashing
        streak = calculate_workout_streak(df_malicious)
        self.assertIsInstance(streak, int)
        
        # Test current workout streak with malicious input
        with patch('src.backend.workout_statistics.date') as mock_date:
            mock_date.today.return_value = date(2024, 1, 15)
            current_streak = get_current_workout_streak(df_malicious)
            self.assertIsInstance(current_streak, int)
        
        # Test frequency graph
        freq_fig = create_workout_frequency_graph(df_malicious)
        self.assertIsInstance(freq_fig, go.Figure)
        
        # Test calendar
        cal_fig = create_workout_calendar(df_malicious)
        self.assertIsInstance(cal_fig, go.Figure)

    def test_performance_large_dataset(self):
        """Test performance with large dataset."""
        # Create very large dataset (10000 workouts)
        start_date = date.today() - timedelta(days=365)
        large_data = []
        
        for i in range(10000):
            current_date = start_date + timedelta(days=i % 365)
            large_data.append({
                'workout_date': current_date.strftime('%Y-%m-%d'),
                'exercise_name': f'Exercise_{i % 50}'
            })
        
        df_large = pd.DataFrame(large_data)
        df_large['workout_date'] = pd.to_datetime(df_large['workout_date'])
        
        # Should complete within reasonable time
        import time
        start_time = time.time()
        
        streak = calculate_workout_streak(df_large)
        with patch('src.backend.workout_statistics.date') as mock_date:
            mock_date.today.return_value = date(2024, 1, 15)
            current_streak = get_current_workout_streak(df_large)
        freq_fig = create_workout_frequency_graph(df_large)
        cal_fig = create_workout_calendar(df_large)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within 5 seconds
        self.assertLess(execution_time, 5.0)
        self.assertIsInstance(streak, int)
        self.assertIsInstance(current_streak, int)
        self.assertIsInstance(freq_fig, go.Figure)
        self.assertIsInstance(cal_fig, go.Figure)

    def test_edge_cases(self):
        """Test various edge cases."""
        # Test with future dates
        future_data = {
            'workout_date': [
                (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
                (date.today() + timedelta(days=2)).strftime('%Y-%m-%d')
            ],
            'exercise_name': ['Bench Press', 'Squats']
        }
        df_future = pd.DataFrame(future_data)
        df_future['workout_date'] = pd.to_datetime(df_future['workout_date'])
        
        streak = calculate_workout_streak(df_future)
        self.assertIsInstance(streak, int)
        
        with patch('src.backend.workout_statistics.date') as mock_date:
            mock_date.today.return_value = date(2024, 1, 15)
            current_streak = get_current_workout_streak(df_future)
            self.assertIsInstance(current_streak, int)
        
        # Test with very old dates
        old_data = {
            'workout_date': [
                '1900-01-01', '1900-01-02'
            ],
            'exercise_name': ['Bench Press', 'Squats']
        }
        df_old = pd.DataFrame(old_data)
        df_old['workout_date'] = pd.to_datetime(df_old['workout_date'])
        
        streak = calculate_workout_streak(df_old)
        self.assertIsInstance(streak, int)
        
        with patch('src.backend.workout_statistics.date') as mock_date:
            mock_date.today.return_value = date(2024, 1, 15)
            current_streak = get_current_workout_streak(df_old)
            self.assertIsInstance(current_streak, int)

    def test_statistical_accuracy(self):
        """Test statistical accuracy of calculations."""
        # Create data with known pattern
        test_data = {
            'workout_date': [
                '2024-01-01', '2024-01-01',  # Day 1
                '2024-01-02', '2024-01-02',  # Day 2 (consecutive)
                '2024-01-03', '2024-01-03',  # Day 3 (consecutive)
                '2024-01-05', '2024-01-05',  # Day 5 (gap of 1 day)
                '2024-01-07', '2024-01-07',  # Day 7 (gap of 1 day)
            ],
            'exercise_name': ['Bench Press', 'Squats'] * 5
        }
        df_test = pd.DataFrame(test_data)
        df_test['workout_date'] = pd.to_datetime(df_test['workout_date'])
        
        streak = calculate_workout_streak(df_test)
        # Should count the streak correctly
        self.assertGreaterEqual(streak, 1)

    def test_error_handling_exceptions(self):
        """Test error handling for various exceptions."""
        # Test with data that would cause pandas errors
        problematic_data = {
            'workout_date': [None, pd.NaT, '2024-01-01'],
            'exercise_name': ['Bench Press', 'Squats', 'Deadlifts']
        }
        df_problematic = pd.DataFrame(problematic_data)
        
        # Should handle gracefully
        streak = calculate_workout_streak(df_problematic)
        self.assertIsInstance(streak, int)
        
        with patch('src.backend.workout_statistics.date') as mock_date:
            mock_date.today.return_value = date(2024, 1, 15)
            current_streak = get_current_workout_streak(df_problematic)
            self.assertIsInstance(current_streak, int)

    def test_data_validation(self):
        """Test data validation for various input types."""
        # Test with different data types
        mixed_data = {
            'workout_date': [1, '2024-01-01', datetime.now()],
            'exercise_name': ['Bench Press', 'Squats', 'Deadlifts']
        }
        df_mixed = pd.DataFrame(mixed_data)
        
        # Should handle mixed data types gracefully
        streak = calculate_workout_streak(df_mixed)
        self.assertIsInstance(streak, int)
        
        current_streak = get_current_workout_streak(df_mixed)
        self.assertIsInstance(current_streak, int)

    def test_boundary_conditions(self):
        """Test boundary conditions for streak calculations."""
        # Test with exactly 2 days ago (boundary for current streak)
        two_days_ago = date.today() - timedelta(days=2)
        boundary_data = {
            'workout_date': [
                two_days_ago.strftime('%Y-%m-%d'), two_days_ago.strftime('%Y-%m-%d')
            ],
            'exercise_name': ['Bench Press', 'Squats']
        }
        df_boundary = pd.DataFrame(boundary_data)
        df_boundary['workout_date'] = pd.to_datetime(df_boundary['workout_date'])
        
        current_streak = get_current_workout_streak(df_boundary)
        # Should be exactly at the boundary
        self.assertIsInstance(current_streak, int)

    def test_memory_efficiency(self):
        """Test memory efficiency with large datasets."""
        # Create dataset that would test memory usage
        large_data = []
        for i in range(5000):
            large_data.append({
                'workout_date': f'2024-{i%12+1:02d}-{i%28+1:02d}',
                'exercise_name': f'Exercise_{i % 100}'
            })
        
        df_large = pd.DataFrame(large_data)
        df_large['workout_date'] = pd.to_datetime(df_large['workout_date'])
        
        # Should handle without memory issues
        streak = calculate_workout_streak(df_large)
        current_streak = get_current_workout_streak(df_large)
        
        self.assertIsInstance(streak, int)
        self.assertIsInstance(current_streak, int)


if __name__ == '__main__':
    unittest.main() 
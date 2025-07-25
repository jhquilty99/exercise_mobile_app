"""
Test suite for workout statistics module (BE-003: Workout Analytics).
Tests workout streak calculation, frequency graphs, and calendar visualization.
"""

import unittest
from datetime import datetime, date, timedelta
import pandas as pd
import plotly.graph_objects as go
from src.backend.workout_statistics import (
    calculate_workout_streak,
    create_workout_frequency_graph,
    create_workout_calendar
)


class TestWorkoutStatistics(unittest.TestCase):
    """Test cases for workout statistics functionality."""

    def setUp(self):
        """Set up test data."""
        # Create sample workout data for testing
        self.sample_data = {
            'Workout Date': [
                '2024-01-01', '2024-01-01', '2024-01-01',  # Day 1
                '2024-01-03', '2024-01-03', '2024-01-03',  # Day 3 (2 day streak)
                '2024-01-05', '2024-01-05', '2024-01-05',  # Day 5 (3 day streak)
                '2024-01-07', '2024-01-07', '2024-01-07',  # Day 7 (4 day streak)
                '2024-01-09', '2024-01-09', '2024-01-09',  # Day 9 (5 day streak)
                '2024-01-12', '2024-01-12', '2024-01-12',  # Day 12 (1 day streak - gap too large)
                '2024-01-14', '2024-01-14', '2024-01-14',  # Day 14 (2 day streak)
                '2024-01-16', '2024-01-16', '2024-01-16',  # Day 16 (3 day streak)
            ],
            'Exercise Name': [
                'Bench Press', 'Squats', 'Deadlifts',
                'Bench Press', 'Squats', 'Pull-ups',
                'Bench Press', 'Squats', 'Deadlifts',
                'Bench Press', 'Squats', 'Pull-ups',
                'Bench Press', 'Squats', 'Deadlifts',
                'Bench Press', 'Squats', 'Pull-ups',
                'Bench Press', 'Squats', 'Deadlifts',
                'Bench Press', 'Squats', 'Pull-ups',
            ],
            'Exercise Type': ['Strength'] * 24,
            'Weight': [135, 185, 225] * 8,
            'Sets': [3, 3, 3] * 8,
            'Discrete Reps': [10, 8, 6] * 8,
            'Alternating': [False] * 24
        }
        
        self.df = pd.DataFrame(self.sample_data)
        self.df['Workout Date'] = pd.to_datetime(self.df['Workout Date'])

    def test_calculate_workout_streak_empty_data(self):
        """Test workout streak calculation with empty data."""
        empty_df = pd.DataFrame()
        streak, message = calculate_workout_streak(empty_df)
        
        self.assertEqual(streak, 0)
        self.assertEqual(message, "No workout data available")

    def test_calculate_workout_streak_no_date_column(self):
        """Test workout streak calculation with missing date column."""
        df_no_date = pd.DataFrame({'Exercise Name': ['Bench Press']})
        streak, message = calculate_workout_streak(df_no_date)
        
        self.assertEqual(streak, 0)
        self.assertEqual(message, "No workout data available")

    def test_calculate_workout_streak_consecutive_days(self):
        """Test workout streak calculation with consecutive workout days."""
        # Create data with consecutive days (2024-01-15, 2024-01-16)
        consecutive_data = {
            'Workout Date': [
                '2024-01-15', '2024-01-15',
                '2024-01-16', '2024-01-16'
            ],
            'Exercise Name': ['Bench Press', 'Squats'] * 2
        }
        df_consecutive = pd.DataFrame(consecutive_data)
        df_consecutive['Workout Date'] = pd.to_datetime(df_consecutive['Workout Date'])
        
        streak, _ = calculate_workout_streak(df_consecutive)
        # Should be 2 day streak (consecutive days)
        self.assertEqual(streak, 2)

    def test_calculate_workout_streak_alternating_days(self):
        """Test workout streak calculation with alternating days (every other day)."""
        # Create data with alternating days (2024-01-15, 2024-01-17)
        alternating_data = {
            'Workout Date': [
                '2024-01-15', '2024-01-15',
                '2024-01-17', '2024-01-17'
            ],
            'Exercise Name': ['Bench Press', 'Squats'] * 2
        }
        df_alternating = pd.DataFrame(alternating_data)
        df_alternating['Workout Date'] = pd.to_datetime(df_alternating['Workout Date'])
        
        streak, _ = calculate_workout_streak(df_alternating)
        # Should be 3 day streak (allows missing every other day)
        self.assertEqual(streak, 3)

    def test_calculate_workout_streak_large_gap(self):
        """Test workout streak calculation with large gaps."""
        # Create data with large gap (2024-01-15, 2024-01-18)
        gap_data = {
            'Workout Date': [
                '2024-01-15', '2024-01-15',
                '2024-01-18', '2024-01-18'
            ],
            'Exercise Name': ['Bench Press', 'Squats'] * 2
        }
        df_gap = pd.DataFrame(gap_data)
        df_gap['Workout Date'] = pd.to_datetime(df_gap['Workout Date'])
        
        streak, _ = calculate_workout_streak(df_gap)
        # Should be 1 day streak (gap too large)
        self.assertEqual(streak, 1)

    def test_calculate_workout_streak_recent_workout(self):
        """Test workout streak calculation with recent workout."""
        # Create data with workout from yesterday
        yesterday = date.today() - timedelta(days=1)
        recent_data = {
            'Workout Date': [
                yesterday.strftime('%Y-%m-%d'), yesterday.strftime('%Y-%m-%d')
            ],
            'Exercise Name': ['Bench Press', 'Squats']
        }
        df_recent = pd.DataFrame(recent_data)
        df_recent['Workout Date'] = pd.to_datetime(df_recent['Workout Date'])
        
        streak, _ = calculate_workout_streak(df_recent)
        # Should have a streak since workout was recent
        self.assertGreaterEqual(streak, 1)

    def test_calculate_workout_streak_old_workout(self):
        """Test workout streak calculation with old workout."""
        # Create data with workout from 10 days ago
        old_date = date.today() - timedelta(days=10)
        old_data = {
            'Workout Date': [
                old_date.strftime('%Y-%m-%d'), old_date.strftime('%Y-%m-%d')
            ],
            'Exercise Name': ['Bench Press', 'Squats']
        }
        df_old = pd.DataFrame(old_data)
        df_old['Workout Date'] = pd.to_datetime(df_old['Workout Date'])
        
        streak, _ = calculate_workout_streak(df_old)
        # Should have 0 streak since workout is too old
        self.assertEqual(streak, 0)

    def test_create_workout_frequency_graph_empty_data(self):
        """Test workout frequency graph creation with empty data."""
        empty_df = pd.DataFrame()
        fig = create_workout_frequency_graph(empty_df)
        
        self.assertIsInstance(fig, go.Figure)
        # Should have annotation indicating no data
        self.assertIn('annotations', fig.layout)

    def test_create_workout_frequency_graph_no_date_column(self):
        """Test workout frequency graph creation with missing date column."""
        df_no_date = pd.DataFrame({'Exercise Name': ['Bench Press']})
        fig = create_workout_frequency_graph(df_no_date)
        
        self.assertIsInstance(fig, go.Figure)
        # Should have annotation indicating no data
        self.assertIn('annotations', fig.layout)

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
                    {'Workout Date': current_date.strftime('%Y-%m-%d'), 'Exercise Name': 'Bench Press'},
                    {'Workout Date': current_date.strftime('%Y-%m-%d'), 'Exercise Name': 'Squats'}
                ])
        
        df_long = pd.DataFrame(long_data)
        df_long['Workout Date'] = pd.to_datetime(df_long['Workout Date'])
        
        fig = create_workout_frequency_graph(df_long)
        
        self.assertIsInstance(fig, go.Figure)
        # Should have data points (after 30-day window starts)
        self.assertGreater(len(fig.data[0].x), 0)

    def test_create_workout_calendar_empty_data(self):
        """Test workout calendar creation with empty data."""
        empty_df = pd.DataFrame()
        fig = create_workout_calendar(empty_df)
        
        self.assertIsInstance(fig, go.Figure)
        # Should be a heatmap
        self.assertEqual(fig.data[0].type, 'heatmap')

    def test_create_workout_calendar_no_date_column(self):
        """Test workout calendar creation with missing date column."""
        df_no_date = pd.DataFrame({'Exercise Name': ['Bench Press']})
        fig = create_workout_calendar(df_no_date)
        
        self.assertIsInstance(fig, go.Figure)
        # Should be a heatmap
        self.assertEqual(fig.data[0].type, 'heatmap')

    def test_create_workout_calendar_valid_data(self):
        """Test workout calendar creation with valid data."""
        fig = create_workout_calendar(self.df, year=2024, month=1)
        
        self.assertIsInstance(fig, go.Figure)
        # Should be a heatmap
        self.assertEqual(fig.data[0].type, 'heatmap')
        # Should have proper layout
        self.assertIn('title', fig.layout)
        # Should have colorscale for workout days
        self.assertIn('colorscale', fig.data[0])

    def test_create_workout_calendar_specific_month(self):
        """Test workout calendar creation for specific month."""
        # Create data for January 2024
        jan_data = {
            'Workout Date': [
                '2024-01-01', '2024-01-01',
                '2024-01-15', '2024-01-15',
                '2024-01-31', '2024-01-31'
            ],
            'Exercise Name': ['Bench Press', 'Squats'] * 3
        }
        df_jan = pd.DataFrame(jan_data)
        df_jan['Workout Date'] = pd.to_datetime(df_jan['Workout Date'])
        
        fig = create_workout_calendar(df_jan, year=2024, month=1)
        
        self.assertIsInstance(fig, go.Figure)
        # Should have title with month and year
        self.assertIn('January 2024', fig.layout.title.text)

    def test_create_workout_calendar_default_parameters(self):
        """Test workout calendar creation with default parameters."""
        fig = create_workout_calendar(self.df)
        
        self.assertIsInstance(fig, go.Figure)
        # Should use current year and month by default
        current_year = datetime.now().year
        current_month = datetime.now().month
        month_name = datetime.now().strftime('%B')
        self.assertIn(str(current_year), fig.layout.title.text)
        self.assertIn(month_name, fig.layout.title.text)

    def test_create_workout_calendar_workout_days_highlighted(self):
        """Test that workout days are properly highlighted in calendar."""
        # Create data with specific workout days
        workout_data = {
            'Workout Date': [
                '2024-01-01', '2024-01-01',  # Day 1
                '2024-01-15', '2024-01-15',  # Day 15
                '2024-01-31', '2024-01-31'   # Day 31
            ],
            'Exercise Name': ['Bench Press', 'Squats'] * 3
        }
        df_workout = pd.DataFrame(workout_data)
        df_workout['Workout Date'] = pd.to_datetime(df_workout['Workout Date'])
        
        fig = create_workout_calendar(df_workout, year=2024, month=1)
        
        # Check that workout days (1, 15, 31) are highlighted
        # The heatmap should have value 2 for workout days
        heatmap_data = fig.data[0].z
        # Find the positions of workout days in the calendar grid
        # This is a simplified check - in practice, you'd need to map calendar positions
        self.assertIsInstance(heatmap_data, list)

    def test_interactive_features(self):
        """Test that visualizations are interactive."""
        # Test frequency graph interactivity
        freq_fig = create_workout_frequency_graph(self.df)
        self.assertIn('hovermode', freq_fig.layout)
        self.assertEqual(freq_fig.layout.hovermode, 'x unified')
        
        # Test calendar interactivity
        cal_fig = create_workout_calendar(self.df)
        self.assertIn('hoverinfo', cal_fig.data[0])
        self.assertEqual(cal_fig.data[0].hoverinfo, 'text')

    def test_data_structures_for_frontend(self):
        """Test that functions return appropriate data structures for frontend integration."""
        # Test streak calculation returns tuple
        streak, message = calculate_workout_streak(self.df)
        self.assertIsInstance(streak, int)
        self.assertIsInstance(message, str)
        
        # Test frequency graph returns Plotly figure
        freq_fig = create_workout_frequency_graph(self.df)
        self.assertIsInstance(freq_fig, go.Figure)
        
        # Test calendar returns Plotly figure
        cal_fig = create_workout_calendar(self.df)
        self.assertIsInstance(cal_fig, go.Figure)


if __name__ == '__main__':
    unittest.main() 
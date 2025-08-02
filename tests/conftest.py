"""
Shared test fixtures for the Exercise Mobile App backend tests.

This module provides common fixtures that can be used across all test modules
to ensure consistency and reduce code duplication.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock


@pytest.fixture
def sample_workout_data():
    """Standard sample workout data for tests."""
    return pd.DataFrame({
        'detailed_exercise_name': ['Bench Press', 'Squat', 'Deadlift', 'Bench Press', 'Squat', 'Bench Press'],
        'weight': [135, 185, 225, 145, 195, 155],
        'sets': [3, 3, 3, 3, 3, 3],
        'reps': [10, 8, 5, 12, 6, 11],
        'alternating': [False, False, False, False, False, False],
        'workout_date': [
            datetime.now() - timedelta(days=1),
            datetime.now() - timedelta(days=2),
            datetime.now() - timedelta(days=3),
            datetime.now() - timedelta(days=4),
            datetime.now() - timedelta(days=5),
            datetime.now() - timedelta(days=6)
        ]
    })


@pytest.fixture
def sample_workout_data_alternating():
    """Sample workout data with alternating exercises."""
    return pd.DataFrame({
        'detailed_exercise_name': ['Dumbbell Curl', 'Dumbbell Curl', 'Bench Press'],
        'weight': [25, 30, 135],
        'sets': [3, 3, 3],
        'reps': [12, 10, 10],
        'alternating': [True, True, False],
        'workout_date': [
            datetime.now() - timedelta(days=1),
            datetime.now() - timedelta(days=2),
            datetime.now() - timedelta(days=3)
        ]
    })


@pytest.fixture
def sample_workout_data_with_dates():
    """Sample workout data with various dates for timeframe testing."""
    return pd.DataFrame({
        'detailed_exercise_name': ['Bench Press', 'Squat', 'Deadlift', 'Bench Press'],
        'weight': [135, 185, 225, 145],
        'sets': [3, 3, 3, 3],
        'reps': [10, 8, 5, 12],
        'alternating': [False, False, False, False],
        'workout_date': [
            datetime.now() - timedelta(days=1),  # Recent
            datetime.now() - timedelta(days=5),  # Recent
            datetime.now() - timedelta(days=10), # Recent
            datetime.now() - timedelta(days=20)  # Older
        ]
    })


@pytest.fixture
def large_workout_dataset():
    """Large dataset for performance testing."""
    n_records = 1000
    exercises = ['Bench Press', 'Squat', 'Deadlift', 'Overhead Press', 'Row', 'Pull-up', 'Dip']
    
    return pd.DataFrame({
        'detailed_exercise_name': np.random.choice(exercises, n_records),
        'weight': np.random.randint(50, 500, n_records),
        'sets': np.random.randint(1, 5, n_records),
        'reps': np.random.randint(5, 20, n_records),
        'alternating': np.random.choice([True, False], n_records),
        'workout_date': [
            datetime.now() - timedelta(days=i) for i in range(n_records)
        ]
    })


@pytest.fixture
def mock_external_api():
    """Standard mock for external API dependencies."""
    mock_api = Mock()
    # Configure standard responses
    mock_api.get_data.return_value = {
        'exercises': [
            {'name': 'Bench Press', 'category': 'Push'},
            {'name': 'Squat', 'category': 'Legs'},
            {'name': 'Deadlift', 'category': 'Pull'}
        ]
    }
    mock_api.authenticate.return_value = True
    return mock_api


@pytest.fixture
def mock_file_system():
    """Standard mock for file system operations."""
    mock_fs = Mock()
    mock_fs.read_file.return_value = "sample data"
    mock_fs.write_file.return_value = True
    mock_fs.file_exists.return_value = True
    return mock_fs


@pytest.fixture
def sample_invalid_data():
    """Sample data with various invalid inputs for testing error handling."""
    return pd.DataFrame({
        'detailed_exercise_name': ['Bench Press', 'Squat', None, '', '   '],
        'weight': [135, -185, np.nan, float('inf'), float('-inf')],
        'sets': [3, 0, -3, np.nan, 999999],
        'reps': [10, -8, 0, np.nan, 1000],
        'alternating': [False, False, None, True, False],
        'workout_date': [
            datetime.now() - timedelta(days=1),
            datetime.now() - timedelta(days=2),
            None,
            datetime.now() + timedelta(days=1),  # Future date
            datetime.now() - timedelta(days=365)  # Very old date
        ]
    })


@pytest.fixture
def sample_malicious_data():
    """Sample data with malicious inputs for security testing."""
    return pd.DataFrame({
        'detailed_exercise_name': [
            "'; DROP TABLE exercises; --",
            "<script>alert('xss')</script>",
            "../../../etc/passwd",
            "javascript:alert('xss')",
            "'; SELECT * FROM users; --"
        ],
        'weight': [135, 185, 225, 145, 155],
        'sets': [3, 3, 3, 3, 3],
        'reps': [10, 8, 5, 12, 11],
        'alternating': [False, False, False, False, False],
        'workout_date': [
            datetime.now() - timedelta(days=1),
            datetime.now() - timedelta(days=2),
            datetime.now() - timedelta(days=3),
            datetime.now() - timedelta(days=4),
            datetime.now() - timedelta(days=5)
        ]
    })


@pytest.fixture
def sample_edge_case_data():
    """Sample data with edge cases for boundary testing."""
    return pd.DataFrame({
        'detailed_exercise_name': ['A', 'B', 'C', 'D', 'E'],
        'weight': [0, 1, 999999, 2**31 - 1, 2**63 - 1],
        'sets': [0, 1, 999, 2**31 - 1, 2**63 - 1],
        'reps': [0, 1, 999, 2**31 - 1, 2**63 - 1],
        'alternating': [False, True, False, True, False],
        'workout_date': [
            datetime.now() - timedelta(days=0),  # Today
            datetime.now() - timedelta(days=1),  # Yesterday
            datetime.now() - timedelta(days=365),  # One year ago
            datetime.now() - timedelta(days=3650),  # Ten years ago
            datetime.now() - timedelta(days=36500)  # Hundred years ago
        ]
    })


@pytest.fixture
def sample_single_exercise_data():
    """Sample data with only one exercise type."""
    return pd.DataFrame({
        'detailed_exercise_name': ['Bench Press', 'Bench Press', 'Bench Press'],
        'weight': [135, 145, 155],
        'sets': [3, 3, 3],
        'reps': [10, 12, 11],
        'alternating': [False, False, False],
        'workout_date': [
            datetime.now() - timedelta(days=1),
            datetime.now() - timedelta(days=2),
            datetime.now() - timedelta(days=3)
        ]
    })


@pytest.fixture
def sample_empty_data():
    """Sample empty DataFrame for testing empty data handling."""
    return pd.DataFrame(columns=[
        'detailed_exercise_name', 'weight', 'sets', 'reps', 
        'alternating', 'workout_date'
    ])


@pytest.fixture
def sample_minimal_data():
    """Sample minimal data with single record."""
    return pd.DataFrame({
        'detailed_exercise_name': ['Bench Press'],
        'weight': [135],
        'sets': [3],
        'reps': [10],
        'alternating': [False],
        'workout_date': [datetime.now()]
    })


@pytest.fixture
def sample_dataframe():
    """Standard sample DataFrame for testing (alias for sample_workout_data)."""
    return pd.DataFrame({
        'detailed_exercise_name': ['Bench Press', 'Squat', 'Deadlift', 'Bench Press', 'Squat', 'Bench Press'],
        'weight': [135, 185, 225, 145, 195, 155],
        'sets': [3, 3, 3, 3, 3, 3],
        'reps': [10, 8, 5, 12, 6, 11],
        'alternating': [False, False, False, False, False, False],
        'workout_date': [
            datetime.now() - timedelta(days=1),
            datetime.now() - timedelta(days=2),
            datetime.now() - timedelta(days=3),
            datetime.now() - timedelta(days=4),
            datetime.now() - timedelta(days=5),
            datetime.now() - timedelta(days=6)
        ]
    }) 
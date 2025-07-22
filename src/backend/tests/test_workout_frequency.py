"""
Test script for workout frequency analytics module.
"""

import pandas as pd
from src.backend.workout_frequency import (
    WorkoutFrequencyAnalyzer,
    calculate_exercise_frequency,
    rank_exercises_by_frequency,
    calculate_percentage_breakdown,
    get_frequency_summary
)

def create_sample_data():
    """Create sample workout data for testing."""
    sample_data = {
        'Workout Date': [
            '2024-01-01', '2024-01-01', '2024-01-01',
            '2024-01-03', '2024-01-03', '2024-01-03',
            '2024-01-05', '2024-01-05', '2024-01-05',
            '2024-01-07', '2024-01-07', '2024-01-07',
            '2024-01-09', '2024-01-09', '2024-01-09'
        ],
        'Exercise Name': [
            'Bench Press', 'Squats', 'Deadlifts',
            'Bench Press', 'Squats', 'Pull-ups',
            'Bench Press', 'Squats', 'Deadlifts',
            'Bench Press', 'Squats', 'Pull-ups',
            'Bench Press', 'Squats', 'Deadlifts'
        ],
        'Exercise Type': ['Strength'] * 15,
        'Weight': [135, 185, 225] * 5,
        'Sets': [3, 3, 3] * 5,
        'Discrete Reps': [10, 8, 6] * 5,
        'Alternating': [False] * 15
    }
    
    df = pd.DataFrame(sample_data)
    df['Workout Date'] = pd.to_datetime(df['Workout Date'])
    return df

def test_workout_frequency():
    """Test the workout frequency analytics functionality."""
    print("=== Workout Frequency Analytics Test ===\n")
    
    # Create sample data
    df = create_sample_data()
    print(f"Sample data created with {len(df)} records")
    print(f"Unique exercises: {df['Exercise Name'].unique()}\n")
    
    # Test 1: Basic frequency calculation
    print("1. Testing basic frequency calculation:")
    frequencies = calculate_exercise_frequency(df)
    print(f"Exercise frequencies:\n{frequencies}\n")
    
    # Test 2: Ranking exercises
    print("2. Testing exercise ranking:")
    ranking_df = rank_exercises_by_frequency(df)
    print(f"Exercise rankings:\n{ranking_df}\n")
    
    # Test 3: Percentage breakdown
    print("3. Testing percentage breakdown:")
    percentages = calculate_percentage_breakdown(df)
    print(f"Exercise percentages:\n{percentages}\n")
    
    # Test 4: Comprehensive analysis
    print("4. Testing comprehensive analysis:")
    analyzer = WorkoutFrequencyAnalyzer()
    result = analyzer.analyze_exercise_frequency(df)
    
    print(f"Total exercises: {result.total_exercises}")
    print(f"Total workouts: {result.total_workouts}")
    print(f"Unique exercises: {result.analysis_summary['unique_exercises']}")
    print(f"Most frequent exercise: {result.analysis_summary['most_frequent_exercise']}")
    print(f"Most frequent count: {result.analysis_summary['most_frequent_count']}")
    print(f"Average frequency: {result.analysis_summary['average_frequency']:.2f}")
    print(f"Median frequency: {result.analysis_summary['median_frequency']:.2f}\n")
    
    # Test 5: Top exercises
    print("5. Testing top exercises:")
    top_exercises = analyzer.get_top_exercises(df, top_n=3)
    for exercise in top_exercises:
        print(f"Rank {exercise.rank}: {exercise.exercise_name} - {exercise.frequency} times ({exercise.percentage}%)")
    print()
    
    # Test 6: Exercise rank lookup
    print("6. Testing exercise rank lookup:")
    bench_press_rank = analyzer.get_exercise_rank(df, "Bench Press")
    print(f"Bench Press rank: {bench_press_rank}")
    
    pull_ups_rank = analyzer.get_exercise_rank(df, "Pull-ups")
    print(f"Pull-ups rank: {pull_ups_rank}\n")
    
    # Test 7: Frequency distribution
    print("7. Testing frequency distribution:")
    distribution = analyzer.get_frequency_distribution(df)
    for range_name, count in distribution.items():
        print(f"{range_name}: {count} exercises")
    print()
    
    # Test 8: Summary function
    print("8. Testing summary function:")
    summary = get_frequency_summary(df)
    print(f"Summary: {summary}\n")
    
    print("=== All tests completed successfully! ===")

if __name__ == "__main__":
    test_workout_frequency() 
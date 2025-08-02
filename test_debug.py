from datetime import datetime, date, timedelta
import pandas as pd
from src.backend.workout_statistics import calculate_workout_streak, get_current_workout_streak
from unittest.mock import patch

# Test data for alternating days
mock_today = date(2024, 1, 15)
yesterday = mock_today - timedelta(days=1)  # 2024-01-14
three_days_ago = mock_today - timedelta(days=3)  # 2024-01-12

alternating_data = {
    'workout_date': [
        three_days_ago.strftime('%Y-%m-%d'), three_days_ago.strftime('%Y-%m-%d'),
        yesterday.strftime('%Y-%m-%d'), yesterday.strftime('%Y-%m-%d')
    ],
    'exercise_name': ['Bench Press', 'Squats'] * 2
}

df_alternating = pd.DataFrame(alternating_data)
df_alternating['workout_date'] = pd.to_datetime(df_alternating['workout_date'])

print("Test data:")
print(f"Mock today: {mock_today}")
print(f"Yesterday: {yesterday}")
print(f"Three days ago: {three_days_ago}")
print(f"Workout dates: {df_alternating['workout_date'].dt.date.unique()}")

# Test calculate_workout_streak
streak = calculate_workout_streak(df_alternating)
print(f"\ncalculate_workout_streak result: {streak}")

# Test get_current_workout_streak with mocked date
with patch('src.backend.workout_statistics.date') as mock_date:
    mock_date.today.return_value = mock_today
    current_streak = get_current_workout_streak(df_alternating)
    print(f"get_current_workout_streak result: {current_streak}")
    
    # Debug: Let's check what the function is actually doing
    print(f"\nDebug info:")
    print(f"Mock today: {mock_date.today()}")
    print(f"Latest workout date: {df_alternating['workout_date'].dt.date.max()}")
    print(f"Days since last workout: {(mock_date.today() - df_alternating['workout_date'].dt.date.max()).days}")
    
    # Let's also check what the actual date.today() returns
    import datetime as dt
    print(f"Actual date.today(): {dt.date.today()}")
    print(f"Mocked date.today(): {mock_date.today()}") 
### BE-007: Derive Fields
**As a** frontend engineer
**I want** the dataframe to have all necessary fields derived ahead of time
**So that** I can quickly display that data to the user without computing them again

**Acceptance Criteria:**
- [X] Create 'detailed_exercise_name' column by concatenating 'exercise_type' and 'exercise_name' with a space between
- [X] Drop the 'exercise_name' field
- [X] Create 'volume' column by multiplying 'weight' * 'sets' * 'reps'

**Technical Requirements:**
- Assume that the input dataframe used has the following schema:
```python
{
    'workout_date': datetime.date,
    'exercise_type': str,
    'exercise_name': str,
    'weight': float,
    'sets': int,
    'reps': int,
    'alternating': bool,
}
```
- Ensure the output dataframe has the following schema:
```python
{
    'workout_date': datetime.date,
    'exercise_type': str,
    'detailed_exercise_name': str,
    'weight': float,
    'sets': int,
    'reps': int,
    'alternating': bool,
    'volume': float,
}
```
**Implementation:**
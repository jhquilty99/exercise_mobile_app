### BE-002: Data Validation and Quality Assurance
**As a** backend system  
**I want to** validate and clean workout data  
**So that** I can provide reliable analytics for users

**Acceptance Criteria:**
- [X] Validate required fields 
- [ ] Enforce proper data types
- [ ] Enforce data constraints (non-negative weights, sets, reps)
- [ ] Identify and handle missing/duplicate values
- [X] Remove invalid records
- [ ] Normalize exercise names (case-insensitive)
- [ ] Convert data to standardized WorkoutLog schema

**Technical Requirements:**
- Implement validation rules:
  - `weight_lbs >= 0`
  - `sets >= 0` 
  - `discrete_reps >= 0`
  - `workout_date` is valid date
- Use pandas for data cleaning operations
- Handle data type conversion errors gracefully
- Generate basic validation summary

```python
# Target schema
{
    'workout_date': datetime.date,
    'exercise_type': str,
    'exercise_name': str,
    'weight_lbs': int,
    'sets': int,
    'discrete_reps': int,
    'alternating': bool,
    'total_volume': int  # calculated field
}
```

**Implementation:**
GoogleSheetsExtractor in extraction.py with methods:
- _validate_sheet_structure
- _clean_and_validate_data
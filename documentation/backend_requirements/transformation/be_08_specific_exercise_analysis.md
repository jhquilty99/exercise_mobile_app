### BE-008: Specific Exercise Analysis
**As a** backend system  
**I want to** analyze individual exercise performance over time  
**So that** I can provide detailed progress tracking for specific exercises

**Acceptance Criteria:**
- [ ] Filter data by specific exercise name and return time series data
- [ ] Calculate maximum statistics for the selected exercise:
    - Max Volume with date achieved
    - Max Weight with date achieved  
    - Max Reps with date achieved
    - Max Sets with date achieved
- [ ] Handle cases where no data exists for the selected exercise

**Technical Requirements:**
- Function should take exercise_name and dataframe as arguments
- For max statistics: return dictionary with max values and their corresponding dates
- Use pandas functions where possible for efficient data processing
- Handle missing data gracefully

**Implementation:** 
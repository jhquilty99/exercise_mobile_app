### FE-013: Specific Exercise Analysis Tab
**As a** fitness enthusiast  
**I want** to see detailed views of my exercises over time
**So that** I can evaluate my performance in different exercises over time'

**Acceptance Criteria:**
- [X] Welcoming header with "📊 All Exercise Analysis"
- [X] Brief description explaining this tab is for analyzing all exercises against one another. 
- [X] Key Metrics can be selected from one of the following:
    - Max Volume
    - Max Weight
    - Average Reps
    - Count
- [X] Key Metrics can be filtered according to the timeframe filters:
    - Last 7 days
    - Last 30 days
    - Last 3 months
    - Last 6 months
    - Last year
    - All time
- [X] Displays a table with the key metric calculated for each exercise 


**Technical Requirements:**
- Use Python's streamlit package to build and launch the dashboard
- Rely on native streamlit functions as much as possible
- Backend Integration: Uses the existing analyze_all_exercises() function from backend.workout_frequency
- Streamlit Framework: Built entirely with native Streamlit functions
- Error Handling: Includes try-catch blocks for robust error handling
- Clean, organized layout with clear sections
- Informative insights showing the top-performing exercise
- Responsive table display with proper column formatting
- Helpful error messages if data issues occur

**Implementation:**

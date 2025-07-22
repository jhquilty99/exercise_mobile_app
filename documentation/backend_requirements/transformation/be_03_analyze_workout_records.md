### BE-003: Workout Analytics
**As a** fitness enthusiast  
**I want to** analyze my workout patterns and track my consistency over time  
**So that** I can understand my fitness habits, maintain motivation, and identify areas for improvement

**Acceptance Criteria:**
- [ ] The system can calculate my current workout streak where the logic is as follows:
    - Workout streak is calculated using the latest available workout date.
    - A workout streak can have missing workouts every other day. 
    - For example, data shows the user works out on '2025-05-01' and '2025-05-03' then that is a 3 day streak.
    - For example, data shows the user works out on '2025-05-01' and '2025-05-02' then that is a 2 day streak.
    - For example, data shows the user works out on '2025-05-01' and '2025-05-04' then that is a 1 day streak.
- [ ] The system can generate a line graph showing workout frequency over time. Workout frequency is calculated as the 30 day rolling window of the number of unique workout dates
- [ ] The system can create a calendar visualization highlighting workout days. The visualization is a pop-up that allows user to navigate to different months and years. Workout days are highlighted in green. 
- [ ] All visualizations are interactive and provide hover information

**Technical Requirements:**
- Implement `calculate_workout_streak()` function that returns current streak count
- Implement `create_workout_frequency_graph()` function that generates Plotly line charts
- Implement `create_workout_calendar()` function that creates calendar heatmaps
- Use pandas for data manipulation and date processing
- Use Plotly for line graph
- Return appropriate data structures for frontend integration
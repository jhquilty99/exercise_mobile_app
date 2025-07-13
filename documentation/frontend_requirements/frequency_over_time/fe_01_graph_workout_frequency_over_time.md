### FE-001: 30-Day Rolling Workout Volume Chart
**As a** user  
**I want** to see my workout consistency over time  
**So that** I can track my training frequency

**Acceptance Criteria:**
- Calculate 30-day rolling window of workout counts
- Display line graph with smooth trend
- X-axis: workout_date
- Y-axis: count of workouts in past 30 days
- Include chart title and clear labeling
- Show trend direction (improving/declining)

**Technical Notes:**
- Use pandas rolling window calculations
- Implement proper date range handling
- Ensure smooth line rendering
- Handle edge cases (less than 30 days of data)
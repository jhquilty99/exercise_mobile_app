### FE-007: Weight Progress Line Chart
**As a** user  
**I want** to see my weight progression over time  
**So that** I can track my strength improvements

**Acceptance Criteria:**
- Create line chart with workout_date on X-axis
- Display weight_lbs on Y-axis
- Color-code lines by exercise_name
- Show clear trend lines with data points
- Include chart title and axis labels
- Handle empty data gracefully

**Technical Notes:**
- Use Plotly for interactive charts
- Implement proper date formatting
- Handle multiple exercises with different colors
- Ensure responsive chart sizing
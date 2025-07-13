### FE-008: Most Frequent Workouts Display
**As a** user  
**I want** to see which exercises I do most often  
**So that** I can understand my training focus

**Acceptance Criteria:**
- Create ranked list of exercises by frequency
- Display bar chart visualization
- Show percentage breakdown
- Include total workout count
- Sort by frequency (highest to lowest)

**Technical Notes:**
- Use `st.bar_chart()` or Plotly bar chart
- Calculate frequency percentages
- Implement proper sorting
- Handle ties in frequency
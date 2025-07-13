### FE-009: Maximum Weight Per Exercise
**As a** user  
**I want** to see my personal records for each exercise  
**So that** I can track my strength achievements

**Acceptance Criteria:**
- Display summary table with highest weight per exercise
- Create bar chart of maximum weights
- Show progress indicators (current vs. previous max)
- Include date of personal record
- Sort by weight (highest to lowest)

**Technical Notes:**
- Use `st.dataframe()` for summary table
- Implement progress calculation logic
- Handle exercises with no weight data
- Use color coding for progress indicators
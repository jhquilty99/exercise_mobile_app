### FE-006: Interactive Exercise Filter with Real-time Chart Updates
**As a** user  
**I want** to filter the weight progress chart by exercise and see immediate updates  
**So that** I can focus on specific exercises and explore my data interactively

**Acceptance Criteria:**
- Provide dropdown or multi-select for exercise_name
- Update chart immediately when filter changes (within 2 seconds)
- Show "All Exercises" option
- Display selected exercises clearly
- Handle single vs. multiple exercise selection
- Show loading indicators during updates
- Maintain chart state and zoom levels where possible
- Handle rapid filter changes gracefully

**Technical Notes:**
- Use `st.selectbox()` or `st.multiselect()`
- Implement real-time chart updates using Streamlit's reactive framework
- Maintain filter state in session state
- Implement efficient data filtering and cache filtered datasets
- Use `st.empty()` containers for dynamic updates
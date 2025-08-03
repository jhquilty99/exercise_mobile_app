### FE-012: Overview Tab
**As a** fitness enthusiast  
**I want** to see a comprehensive overview of my workout progress and performance at a glance
**So that** I can quickly understand my fitness journey and identify areas for improvement

**Acceptance Criteria:**
- [X] Welcoming header with "📊 Overview"
- [X] Brief description explaining this is my workout dashboard. Includes purpose and navigation tips. 
- [X] Key metrics displayed in a clean grid layout:
    - Total Workouts 
    - Total Exercises 
- [X] Key Metrics can be filtered according to the timeframe filters:
    - Last 7 days
    - Last 30 days
    - Last 3 months
    - Last 6 months
    - Last year
    - All time

**Technical Requirements:**
- Relies on summary_statistics.py backend function which takes df and timeframe arguments
- Use Python's streamlit package to build and launch the dashboard
- Rely on native streamlit functions as much as possible

**Implementation:**
Implemented as overview.py with one function:
- render_overview_page(df)


### FE-013: Specific Exercise Analysis Tab
**As a** fitness enthusiast  
**I want** to see detailed views of my exercises over time
**So that** I can evaluate my performance in different exercises over time'

**Acceptance Criteria:**
- [ ] Welcoming header with "📊 Specific Exercise Analysis"
- [ ] Brief description explaining this is meant to show the user their progress for particular exercises.
- [ ] Filter to choose one of the existing detailed exercise names
- [ ] Line graph of X over time, with dots connected by green lines. Where X is one of:
    - Volume
    - Weight
    - Reps
    - Sets 
- [ ] Displays statistics on the Max Volume, Weight, Reps, and Sets done for that exercise and the date they were accomplished. 


**Technical Requirements:**
- Use Python's streamlit package to build and launch the dashboard
- Rely on native streamlit functions as much as possible
- Use the plotly library for graphs
- Use streamlit cache to only call the backend again if exercise name changes

**Implementation:**

### BE-003: Exercise Performance Analytics
**As a** backend system  
**I want to** calculate comprehensive exercise performance metrics including weight progression and workout volume  
**So that** I can provide insights into strength gains, workout consistency, and training intensity over time

**Acceptance Criteria:**
- [ ] Calculate maximum weight per exercise over time
- [ ] Identify weight progression trends and detect plateaus
- [ ] Calculate average weight per exercise with statistical measures
- [ ] Generate progress indicators (current vs previous max)
- [ ] Calculate total volume per workout session (weight × sets × reps)
- [ ] Compute rolling 30-day workout frequency and consistency metrics
- [ ] Calculate average volume per exercise and identify workout patterns
- [ ] Handle exercises with no weight data appropriately
- [ ] Handle alternating exercises (divide volume by 2)

**Technical Requirements:**
- Use pandas groupby and aggregation functions for data analysis
- Implement trend analysis algorithms for weight progression
- Calculate statistical measures (mean, median, std dev) for weight data
- Implement volume calculation: `weight × sets × reps`
- Use pandas rolling window for time-based frequency calculations
- Handle missing weight data appropriately
- Calculate volume trends and patterns
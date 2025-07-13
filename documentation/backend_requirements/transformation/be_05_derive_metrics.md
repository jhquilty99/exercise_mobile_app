### BE-005: Derived Metrics Calculation
**As a** backend system  
**I want to** calculate derived metrics from raw workout data  
**So that** I can provide enhanced analytics and insights

**Acceptance Criteria:**
- [ ] Calculate total volume per workout (weight × sets × reps)
- [ ] Compute rolling 30-day workout frequency
- [ ] Calculate maximum weight per exercise
- [ ] Determine most frequent exercises
- [ ] Calculate workout consistency metrics
- [ ] Generate progress indicators (current vs previous max)

**Technical Requirements:**
- Use pandas rolling window functions for time-based calculations
- Implement efficient aggregation functions
- Cache calculated metrics for performance
- Handle edge cases (no previous data, single workouts)
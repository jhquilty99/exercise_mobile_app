### BE-006: Comprehensive Data Filtering System
**As a** backend system  
**I want to** provide filtered workout data by exercise criteria and date ranges  
**So that** I can support interactive filtering and time-based analysis in the frontend

**Acceptance Criteria:**
- [ ] Filter by single exercise name
- [ ] Support multi-select exercise filtering
- [ ] Filter by exercise type/category
- [ ] Filter by specific date range (start_date to end_date)
- [ ] Support relative date ranges (last 30 days, last 6 months)
- [ ] Return filtered data efficiently
- [ ] Maintain data integrity during filtering
- [ ] Support case-insensitive exercise name matching
- [ ] Handle invalid date ranges gracefully
- [ ] Return data sorted by date
- [ ] Support timezone-aware date handling

**Technical Requirements:**
- Use pandas query methods for efficient filtering
- Implement exercise name normalization
- Support partial string matching for exercise names
- Use pandas datetime filtering capabilities
- Implement date range validation
- Support multiple date format inputs
- Handle timezone conversions if needed
- Return filtered data in consistent format
# Product Requirements Document: Streamlit Workout History Dashboard

## 1. Executive Summary

### 1.1 Product Vision
A desktop-based Streamlit web application designed to visualize personal workout history stored in Google Sheets. The application will provide comprehensive analytics for tracking weight progress, workout frequency, and performance metrics over time.

### 1.2 Target Users
- Primary: Individual fitness enthusiasts tracking personal workout data
- Secondary: Anyone needing to visualize time-series fitness data from Google Sheets

### 1.3 Success Metrics
- User engagement: Time spent analyzing workout data
- Data accuracy: Correct visualization of workout trends
- Performance: Fast loading times for data visualization
- Usability: Intuitive interface for data exploration

## 2. Product Overview

### 2.1 Problem Statement
Fitness enthusiasts often track their workouts in spreadsheets but lack effective tools to visualize progress, identify trends, and gain insights from their data. Manual analysis is time-consuming and doesn't provide the interactive experience needed for effective progress tracking.

### 2.2 Solution
A Streamlit-based dashboard that automatically connects to Google Sheets, transforms workout data, and presents it through interactive visualizations and summary metrics.

### 2.3 Key Value Propositions
- **Automated Data Processing**: Seamless integration with Google Sheets
- **Interactive Visualizations**: Dynamic charts for trend analysis
- **Performance Tracking**: Clear metrics for progress monitoring
- **User-Friendly Interface**: No technical expertise required

## 3. Data Architecture

### 3.1 Data Source
- **Primary Source**: Google Sheets
- **Refresh Strategy**: Manual refresh (user-initiated)
- **Data Ownership**: User-controlled personal data

### 3.2 Data Schema
```sql
CREATE TABLE WorkoutLog (
    workout_date DATE NOT NULL,
    exercise_type VARCHAR(50) NOT NULL,
    exercise_name VARCHAR(100) NOT NULL,
    weight_lbs INT CHECK (weight_lbs >= 0),
    sets INT CHECK (sets >= 0),
    discrete_reps INT CHECK (discrete_reps >= 0),
    alternating BOOLEAN DEFAULT FALSE
);
```

### 3.3 Data Quality Requirements
- **Completeness**: Handle missing values gracefully
- **Consistency**: Stable schema with consistent data types
- **Validation**: Enforce data constraints (non-negative weights, sets, reps)
- **Transformation**: Calculate derived metrics from raw data

### 3.4 Data Processing Pipeline
1. **Extraction**: Read data from Google Sheets
2. **Transformation**: 
   - Fill missing values
   - Convert data types
   - Calculate derived metrics
3. **Loading**: Prepare data for visualization

## 4. Functional Requirements

### 4.1 Core Features

#### 4.1.1 Weight Progress Visualization
**Feature**: Line chart showing weight progression over time
- **X-axis**: workout_date
- **Y-axis**: weight_lbs
- **Grouping**: Color-coded by exercise_name
- **Interactivity**: 
  - Filter by exercise_name (dropdown/multi-select)
  - Optional date range selection
- **Display**: Clear trend lines with data points

#### 4.1.2 Rolling Workout Volume
**Feature**: 30-day rolling window workout count
- **X-axis**: workout_date
- **Y-axis**: Count of workouts in past 30 days
- **Calculation**: Rolling sum of unique workout dates
- **Visualization**: Line graph with smooth trend
- **Purpose**: Track workout consistency over time

#### 4.1.3 Summary Metrics Dashboard
**Feature**: Key performance indicators and statistics

**Most Frequent Workouts**:
- Ranked list of exercises by frequency
- Bar chart visualization
- Percentage breakdown

**Max Weight Per Exercise**:
- Summary table showing highest weight for each exercise
- Bar chart of maximum weights
- Progress indicators (current vs. previous max)

### 4.2 Interactivity Requirements

#### 4.2.1 Filtering Capabilities
- **Exercise Filter**: Dropdown or multi-select for exercise_name
- **Date Range**: Optional date slider or range picker
- **Exercise Type**: Filter by exercise category
- **Real-time Updates**: Charts update immediately upon filter changes

#### 4.2.2 Responsive Design
- **Desktop-First**: Optimized for desktop viewing
- **Layout**: Clean, organized dashboard layout
- **Navigation**: Intuitive menu structure
- **Loading States**: Clear indicators during data processing

## 5. Technical Requirements

### 5.1 Technology Stack
- **Frontend**: Streamlit (Python web framework)
- **Data Processing**: Pandas, NumPy
- **Google Sheets Integration**: gspread or pandas + gsheets
- **Visualization**: Plotly, Matplotlib, or Streamlit native charts
- **Deployment**: Local or cloud hosting

### 5.2 Performance Requirements
- **Data Loading**: < 5 seconds for typical dataset sizes
- **Chart Rendering**: < 2 seconds for interactive updates
- **Memory Usage**: Efficient handling of datasets up to 10,000 records
- **Browser Compatibility**: Modern browsers (Chrome, Firefox, Safari, Edge)

### 5.3 Security Requirements
- **Data Privacy**: No data storage on external servers
- **Authentication**: Not required (personal use)
- **API Security**: Secure Google Sheets API integration
- **Local Processing**: All data processing occurs locally

### 5.4 Scalability Considerations
- **Data Volume**: Support for datasets up to 10,000 workout records
- **Concurrent Users**: Single-user application
- **Future Growth**: Architecture should support additional data sources

## 6. User Experience Requirements

### 6.1 User Interface Design
- **Dashboard Layout**: Clean, organized grid layout
- **Color Scheme**: Professional, fitness-themed colors
- **Typography**: Readable fonts with appropriate hierarchy
- **Spacing**: Adequate white space for visual clarity

### 6.2 User Workflow
1. **Setup**: Configure Google Sheets connection
2. **Data Refresh**: Manual refresh of workout data
3. **Exploration**: Interactive filtering and visualization
4. **Analysis**: Review trends and performance metrics

### 6.3 Accessibility
- **Keyboard Navigation**: Basic keyboard support
- **Screen Reader**: Basic compatibility
- **Color Contrast**: Sufficient contrast for readability
- **Font Scaling**: Responsive to browser zoom settings

## 7. Non-Functional Requirements

### 7.1 Reliability
- **Error Handling**: Graceful handling of data errors
- **Data Validation**: Robust validation of input data
- **Fallback Mechanisms**: Alternative displays for missing data
- **Logging**: Basic error logging for troubleshooting

### 7.2 Maintainability
- **Code Organization**: Modular, well-documented code
- **Configuration**: External configuration for settings
- **Documentation**: Clear setup and usage instructions
- **Version Control**: Proper source code management

### 7.3 Usability
- **Learning Curve**: Minimal learning required
- **Documentation**: Clear help and guidance
- **Error Messages**: User-friendly error descriptions
- **Onboarding**: Simple setup process

## 8. Constraints and Limitations

### 8.1 Technical Constraints
- **Platform**: Desktop-only (no mobile optimization)
- **Data Source**: Limited to Google Sheets
- **Real-time**: Manual refresh only (no real-time updates)
- **Export**: No data export functionality

### 8.2 Business Constraints
- **Scope**: Personal use only
- **Authentication**: No user management system
- **Integration**: No third-party fitness tracker integration
- **Reporting**: No automated report generation

## 9. Out of Scope Features

### 9.1 Explicitly Excluded
- **Mobile Support**: No mobile optimization or responsive design
- **Data Export**: No functionality to export charts or data
- **Machine Learning**: No predictive analytics or ML features
- **Automated Reports**: No scheduled report generation
- **Workout Journaling**: No note-taking or journaling features
- **Social Features**: No sharing or social media integration
- **Goal Tracking**: No goal setting or milestone tracking
- **Third-party Integration**: No integration with fitness trackers

### 9.2 Future Considerations (Optional)
- **Comparative Analytics**: Progress comparison over time periods
- **Goal Tracking**: Personal goal setting and milestone alerts
- **Fitness Tracker Integration**: APIs for Strava, Fitbit, etc.
- **Advanced Analytics**: Statistical analysis and insights
- **Data Export**: Chart and data export capabilities
- **Mobile Support**: Responsive design for mobile devices

## 10. Success Criteria

### 10.1 Functional Success
- [ ] Successfully connects to Google Sheets
- [ ] Displays weight progress charts with filtering
- [ ] Shows rolling 30-day workout volume
- [ ] Provides summary metrics for exercises
- [ ] Handles data errors gracefully

### 10.2 Performance Success
- [ ] Loads data within 5 seconds
- [ ] Updates charts within 2 seconds
- [ ] Handles datasets up to 10,000 records
- [ ] Maintains responsive UI during processing

### 10.3 User Experience Success
- [ ] Intuitive interface requiring minimal training
- [ ] Clear data visualization and insights
- [ ] Smooth interaction with filters and charts
- [ ] Professional appearance and layout

## 11. Implementation Phases

### 11.1 Phase 1: Core Infrastructure
- Google Sheets integration
- Basic data processing pipeline
- Simple weight progress chart

### 11.2 Phase 2: Enhanced Visualizations
- Rolling workout volume chart
- Summary metrics dashboard
- Interactive filtering

### 11.3 Phase 3: Polish and Optimization
- UI/UX improvements
- Performance optimization
- Error handling and validation

## 12. Risk Assessment

### 12.1 Technical Risks
- **Google Sheets API Changes**: Mitigation through stable API usage
- **Data Format Changes**: Robust data validation and error handling
- **Performance Issues**: Efficient data processing and caching

### 12.2 User Experience Risks
- **Complex Setup**: Clear documentation and setup guides
- **Data Accuracy**: Validation and error checking
- **Usability Issues**: User testing and feedback incorporation

## 13. Conclusion

This Streamlit Workout History Dashboard will provide users with a powerful, interactive tool for analyzing their fitness progress. By focusing on core visualization needs and maintaining a simple, effective interface, the application will deliver significant value for personal fitness tracking while remaining within scope and technical constraints.

The modular architecture and clear separation of concerns will ensure maintainability and provide a foundation for future enhancements while meeting all current requirements for a desktop-based workout analytics solution.

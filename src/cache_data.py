import streamlit as st
from backend.extraction import GoogleSheetsExtractor
from backend.summary_statistics import calculate_total_rows, calculate_distinct_dates
from frontend.layout import create_dashboard_layout
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_workout_data():
    """
    Load workout data from Google Sheets with caching.
    This function will only run once per hour or when parameters change.
    """
    credentials_path = "google_sheets_service_account.json"
    spreadsheet_id = "1vC6qXrz-BmviRIEcI3uU9yfW0I44iYuZF_XzEyok2Es"
    sheet_name = "Fact Exercise 2"
    range_name = "A1:G1000"
    
    try:
        # Create extractor
        extractor = GoogleSheetsExtractor(credentials_path)
        
        # Test connection
        if extractor.test_connection(spreadsheet_id):
            logger.info("Connection successful!")
            
            # Extract data
            df, stats = extractor.extract_data(
                spreadsheet_id=spreadsheet_id,
                sheet_name=sheet_name,
                range_name=range_name
            )
            
            logger.info(f"Extracted {len(df)} records")
            logger.info(f"Stats: {stats}")
            
            total_exercises = calculate_total_rows(df)
            total_workouts = calculate_distinct_dates(df)

            return df, stats, total_exercises, total_workouts
            
    except Exception as e:
        logger.error(f"Error: {e}")
        st.error(f"Failed to load data: {e}")
        return None, None, None, None
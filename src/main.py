from cache_data import load_workout_data

from frontend.layout import create_dashboard_layout
import logging
import streamlit as st

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Load data (cached)
    df, stats, total_exercises, total_workouts = load_workout_data()
    
    if df is not None:        
        # Create dashboard
        create_dashboard_layout(total_workouts, total_exercises)
    else:
        st.error("Unable to load workout data. Please check your connection and try again.")
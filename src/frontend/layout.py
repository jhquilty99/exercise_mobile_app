import streamlit as st
from frontend.overview import render_overview_page
from frontend.all_exercise import render_all_exercise_analysis_page
from frontend.workout import render_workout_analysis_page
from frontend.specific_exercise import render_specific_exercise_analysis_page
#from frontend.specific_exercise_tab.specific_exercise import render_weight_progress_page
#from frontend.all_exercises_tab.all_exercises import render_summary_metrics_page

def create_dashboard_layout(df):
    """
    Creates the main dashboard layout with title, subtitle, and sidebar navigation.
    Implements FE-003: Application Layout and Navigation
    """
    
    # Set page configuration
    st.set_page_config(
        page_title="Workout History Dashboard",
        page_icon="💪",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Main title and subtitle
    st.title("Workout History Dashboard")
    st.markdown("*Track your fitness journey with detailed workout analytics and progress insights*")
    
    # Sidebar navigation
    st.sidebar.header("Navigation")
    
    # Navigation options
    with st.sidebar:
        page = st.radio(
            "Choose a section:",
            ["Overview", "All Exercise Analysis", "Workout Analysis", "Specific Exercise Analysis"]
        )
    
    # Display content based on selected page
    if page == "Overview":
        render_overview_page(df)
        
    elif page == "All Exercise Analysis":
        render_all_exercise_analysis_page(df)
        
    elif page == "Workout Analysis":
        render_workout_analysis_page(df)
        
    elif page == "Specific Exercise Analysis":
        render_specific_exercise_analysis_page(df)
        
    #elif page == "Specific Exercise":
    #    render_weight_progress_page(df)
        
    #elif page == "All Exercises":
    #    render_summary_metrics_page(df)

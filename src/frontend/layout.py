import streamlit as st
from .overview import render_overview_page
from .weight_progress import render_weight_progress_page
from .workout_volume import render_workout_volume_page
from .summary_metrics import render_summary_metrics_page

def create_dashboard_layout(total_workouts, total_exercises):
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
            ["Overview", "Weight Progress", "Workout Volume", "Summary Metrics"]
        )
    
    # Display content based on selected page
    if page == "Overview":
        render_overview_page(total_workouts, total_exercises)
        
    elif page == "Weight Progress":
        render_weight_progress_page()
        
    elif page == "Workout Volume":
        render_workout_volume_page()
        
    elif page == "Summary Metrics":
        render_summary_metrics_page()

def main():
    """
    Main function to run the dashboard
    """
    total_workouts = 100
    total_exercises = 1000
    create_dashboard_layout(total_workouts, total_exercises)

if __name__ == "__main__":
    main()

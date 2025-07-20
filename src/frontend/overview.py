import streamlit as st

def render_overview_page(total_workouts, total_exercises):
    """
    Renders the Overview page content.
    Provides a high-level summary of the fitness journey.
    """
    st.header("📊 Overview")
    st.write("Welcome to your workout dashboard! This section provides a high-level summary of your fitness journey.")
    st.info("Select a section from the sidebar to explore detailed analytics.")
    
    # Placeholder for overview content
    st.subheader("Quick Stats")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(label="Total Workouts", value=total_workouts, delta="0")
    
    with col2:
        st.metric(label="Total Exercises", value=total_exercises, delta="0")
    
    # Placeholder for recent activity
    st.subheader("Recent Activity")
    st.write("Recent workout activity will be displayed here.")
    
    # Placeholder for progress summary
    st.subheader("Progress Summary")
    st.write("Overall progress summary and trends will be displayed here.")

if __name__ == "__main__":
    render_overview_page() 
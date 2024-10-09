import streamlit as st
from plots import moving_average, max_weight, total_volume
import pandas as pd

# Streamlit tabs
tab1, tab2 = st.tabs(["Overall", "By Exercise"])

# Data Loading and Preprocessing
df = pd.read_excel('working_out_sample_10_09_2024.xlsx', sheet_name="Fact Exercise")
df.rename(columns={
    'Workout Date':'date',
    'Exercise Name':'name',
    'Weight (lbs)':'weight',
    'Sets':'sets',
    'Discrete Reps':'reps'
}, inplace=True)

# Ensure the 'Date' column is in datetime format
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Drop rows with missing or invalid dates
df = df.dropna(subset=['date'])


# Filter exercises with at least 2 non-null weights
valid_exercises = df.groupby('name')['weight'].count()
valid_exercises = valid_exercises[valid_exercises >= 2].index

# Keep only the valid exercises in the dataframe
exercise_list = df[df['name'].isin(valid_exercises)]['name'].unique()


# Plotting
# Moving Average of Overall Workouts
with tab1:
    st.header("Overall Workouts")
    date_ranges = (14,30,60)
    selected_date_range = st.selectbox("Select a Date Range", date_ranges)
    selected_smooth = st.selectbox("Smooth Plot?", [True, False])
    fig = moving_average(df, selected_date_range, selected_smooth)
    st.pyplot(fig)

# Plot of Individual Exercises 
with tab2:
    st.header("Individual Exercise Progress")
    selected_exercise = st.selectbox("Select an Exercise", exercise_list)
    fig = max_weight(df, selected_exercise)
    st.pyplot(fig)
    fig = total_volume(df, selected_exercise)
    st.pyplot(fig)
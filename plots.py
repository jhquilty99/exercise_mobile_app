import matplotlib.pyplot as plt
import pandas as pd
from scipy.ndimage import gaussian_filter1d

def moving_average(df, selected_date_range, smooth):
    # Create a complete date range from the first to the last date in the dataset
    date_range = pd.date_range(start=df['date'].min(), end=df['date'].max())

    # Group the data by date and count the rows for each date
    df_count = df.groupby(df['date'].dt.date).size().reset_index(name='Row Count')

    # Convert 'date' column back to datetime format for merging with full date range
    df_count['date'] = pd.to_datetime(df_count['date'])

    # Create a new dataframe with the full date range
    full_date_range = pd.DataFrame({'date': date_range})

    # Merge the original data with the complete date range, filling missing counts with 0
    df_full = pd.merge(full_date_range, df_count, on='date', how='left').fillna(0)

    # Calculate the 30-day moving average of the row count
    df_full['Moving Count'] = df_full['Row Count'].rolling(window=selected_date_range).mean()

    # Apply Gaussian smoothing if specified
    if smooth:
        df_full['Moving Count'] = gaussian_filter1d(df_full['Moving Count'], sigma=3)

    # Plot the data using matplotlib
    fig, ax = plt.subplots()
    ax.plot(df_full['date'], df_full['Moving Count'], label=f'{selected_date_range} Day Moving Count')

    # Set labels and title
    ax.set_xlabel('Workout Date')
    ax.set_ylabel('Row Count')
    ax.set_title(f'{selected_date_range} Day Moving Count of Distinct Exercises Over Time')
    ax.set_ylim(bottom=0)

    plt.xticks(rotation=45)

    return fig

def max_weight (df, selected_exercise):
    # Filter the dataframe based on the selected exercise
    df_filtered = df[df['name'] == selected_exercise].copy()

    # Group by Date and calculate the max weight for the selected exercise
    df_max_weight = df_filtered.groupby(df_filtered['date'].dt.date)['weight'].max().reset_index()

    # Convert the date back to datetime format for plotting
    df_max_weight['date'] = pd.to_datetime(df_max_weight['date'])

    # Create a scatter plot
    fig, ax = plt.subplots()
    ax.scatter(df_max_weight['date'], df_max_weight['weight'], label='Max Weight', color='blue', alpha=0.6)

    # Apply Gaussian smoothing if specified
    smoothed_weights = gaussian_filter1d(df_max_weight['weight'], sigma=1)
    ax.plot(df_max_weight['date'], smoothed_weights, label='Smoothed Trend', color='orange')

    # Calculate the maximum weight of all time
    max_weight_all_time = df_max_weight['weight'].max()

    # Add a dotted horizontal line for the maximum weight of all time
    ax.axhline(y=max_weight_all_time, color='grey', linestyle='--', label='Max Weight of All Time')

    # Set labels and title
    ax.set_xlabel('Workout Date')
    ax.set_ylabel('Max Weight (lbs)')
    ax.set_title(f'Max Weight Over Time for {selected_exercise}')
    ax.set_ylim(bottom=0)
    ax.legend()

    plt.xticks(rotation=45)

    return fig

def total_volume (df, selected_exercise):
     # Filter the dataframe based on the selected exercise
    df_filtered = df[df['name'] == selected_exercise].copy()

    # Calculate total volume (weight * reps * sets) for each entry
    df_filtered['total_volume'] = df_filtered['weight'] * df_filtered['reps'] * df_filtered['sets']

    # Group by Date and calculate the sum of total volume for the selected exercise
    df_volume = df_filtered.groupby(df_filtered['date'].dt.date)['total_volume'].sum().reset_index()

    # Convert the date back to datetime format for plotting
    df_volume['date'] = pd.to_datetime(df_volume['date'])

    # Create a scatter plot
    fig, ax = plt.subplots()
    ax.scatter(df_volume['date'], df_volume['total_volume'], label='Total Volume', color='blue', alpha=0.6)

    # Apply Gaussian smoothing if specified
    smoothed_volume = gaussian_filter1d(df_volume['total_volume'], sigma=2)
    ax.plot(df_volume['date'], smoothed_volume, label='Smoothed Trend', color='orange')

    # Calculate the maximum volume of all time
    max_volume_all_time = df_volume['total_volume'].max()

    # Add a dotted horizontal line for the maximum volume of all time
    ax.axhline(y=max_volume_all_time, color='red', linestyle='--', label='Max Volume of All Time')

    # Set labels and title
    ax.set_xlabel('Workout Date')
    ax.set_ylabel('Total Volume (lbs)')
    ax.set_title(f'Total Volume Over Time for {selected_exercise}')
    ax.set_ylim(bottom=0)
    ax.legend()

    plt.xticks(rotation=45)

    return fig
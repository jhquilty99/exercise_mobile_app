# Exercise Mobile Application
Application for visualizing current exercise progress on the fly.

## Problem

It's hard to figure out how much progress I've made recently and overall with my regards to workout journey. I can do some basic visualizations in Google sheets, however that is limited and not mobile friendly. 

## Solution

Develop a read only app that pulls in workout data and visualizes it a mobile friendly manner available at exercise.haydenquilty.com. This visualizes the moving average of workout days and weight progression on individual exercises. The solution is highly extensible and can be expanded to include workout summaries, recommendations, correlations, and so on. 

## Value

With a custom mobile-friendly workout visualizer, I can better understand my progress including areas of strength and weakness and build exhibits that support my growth. 

## Next Steps

1. Download exercise data and manually upload to python
2. Create bokeh graphs that visualizes the two values I'm interested in.
3. Wrap these bokeh graphs in a streamlit app with filters for dynamic visualizations.

# Additional Information

## Getting Started

1. Clone the repository and start Docker daemon
2. Run "docker build -t exercise_app:latest ."
3. Run "docker run --rm -p 8501:8501 exercise_app:latest"
4. Navigate to localhost:8501 in your browser to see the application

## Detailed Solution

The application displays has three tabs:
1. Workout View: Moving average of daily exercise count by date.
2. Strength Exercise View: Trendline for max weight and total volume by date. Also displays the top and bottom 10 exercises in terms of 30 day % change in volume.
3. Endurance Exercise View: Trendline for max duration by date. 
4. Speed Excercise View: Trendline for min duration by date. 

## Glossary

We use specific definitions for terms associated with exercising in this data.
* Workout: A session of vigorous physical exercise or training.
* Exercise: A particular activity requiring physical effort, carried out to sustain or improve health and fitness.
    * Strength Exercise: An exercise with the goal of maximizing rep weight.
    * Endurance Exercise: An exercise with the goal of maximizing duration.
    * Speed Exercise: An exercise with the goal of minimizing duration.
* Set Family: A group of sets from a particular exercise performed in a row. This terms was borrowed from math for the purposes of grouping sets together. 
* Set: A group of reps from a particular exercise performed in a row.
* Rep: A single execution of an exercise.
* Weight: The mass of the object moved during a strength exercise, excluding bodyweight.
* Volume: Weight * Sets * Reps. Represents the cumulative amount of mass moved during a set family.
* Duration: Total time between starting and completing the rep. 
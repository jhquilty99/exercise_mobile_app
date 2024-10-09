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


## Getting Started
1. Clone the repository and start Docker daemon
2. Run "docker build -t exercise_app:latest ."
3. Run "docker run --rm -p 8501:8501 exercise_app:latest"
4. Navigate to localhost:8501 in your browser to see the application

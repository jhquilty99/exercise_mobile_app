"""
Frontend package for the Workout History Dashboard.
Contains all UI components and page layouts.
"""

from .layout import create_dashboard_layout
from .overview import render_overview_page
from .weight_progress import render_weight_progress_page
from .workout_volume import render_workout_volume_page
from .summary_metrics import render_summary_metrics_page

__all__ = [
    'create_dashboard_layout',
    'render_overview_page',
    'render_weight_progress_page',
    'render_workout_volume_page',
    'render_summary_metrics_page'
] 
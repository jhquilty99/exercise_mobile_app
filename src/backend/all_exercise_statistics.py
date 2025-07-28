"""
Workout Frequency Analytics Module

This module provides comprehensive analytics for workout frequency patterns,
including exercise frequency calculations, rankings, and time-based filtering.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, date, timedelta
from dataclasses import dataclass
import logging
from .filter import filter_dataframe_by_timeframe

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ExerciseRanking:
    """Data class for exercise ranking information."""
    rank: int
    exercise_name: str
    frequency: int
    percentage: float


@dataclass
class FrequencyAnalysisResult:
    """Results of comprehensive frequency analysis."""
    total_exercises: int
    total_workouts: int
    analysis_summary: Dict[str, Any]
    frequency_data: pd.DataFrame
    ranking_data: pd.DataFrame


class WorkoutFrequencyAnalyzer:
    """
    Comprehensive analyzer for workout frequency patterns.
    
    Provides methods for:
    - Calculating exercise frequencies
    - Ranking exercises by frequency
    - Time-based filtering
    - Statistical analysis of workout patterns
    """
    
    def __init__(self):
        """Initialize the analyzer."""
        self.key_metrics = {
            'Max Volume': 'max_volume',
            'Max Weight': 'max_weight',
            'Average Reps': 'avg_reps',
            'Count': 'count'
        }
    
    def analyze_exercise_frequency(self, df: pd.DataFrame) -> FrequencyAnalysisResult:
        """
        Perform comprehensive frequency analysis on workout data.
        
        Args:
            df: DataFrame with workout data
            
        Returns:
            FrequencyAnalysisResult with analysis summary and data
        """
        logger.info("Starting comprehensive frequency analysis")
        
        # Calculate basic frequencies
        frequencies = calculate_exercise_frequency(df)
        
        # Calculate total metrics
        total_exercises = len(frequencies)
        total_workouts = frequencies['frequency'].sum()
        
        # Create analysis summary
        analysis_summary = {
            'unique_exercises': total_exercises,
            'most_frequent_exercise': frequencies.iloc[0]['detailed_exercise_name'],
            'most_frequent_count': frequencies.iloc[0]['frequency'],
            'average_frequency': frequencies['frequency'].mean(),
            'median_frequency': frequencies['frequency'].median(),
            'total_workouts': total_workouts
        }
        
        # Create ranking data
        ranking_data = rank_exercises_by_frequency(df)
        
        return FrequencyAnalysisResult(
            total_exercises=total_exercises,
            total_workouts=total_workouts,
            analysis_summary=analysis_summary,
            frequency_data=frequencies,
            ranking_data=ranking_data
        )
    
    def get_top_exercises(self, df: pd.DataFrame, top_n: int = 5) -> List[ExerciseRanking]:
        """
        Get top N exercises by frequency.
        
        Args:
            df: DataFrame with workout data
            top_n: Number of top exercises to return
            
        Returns:
            List of ExerciseRanking objects
        """
        frequencies = calculate_exercise_frequency(df)
        percentages = calculate_percentage_breakdown(df)
        
        top_exercises = []
        for i, (_, row) in enumerate(frequencies.head(top_n).iterrows(), 1):
            exercise_name = row['detailed_exercise_name']
            frequency = row['frequency']
            percentage = percentages.get(exercise_name, 0.0)
            
            top_exercises.append(ExerciseRanking(
                rank=i,
                exercise_name=exercise_name,
                frequency=frequency,
                percentage=percentage
            ))
        
        return top_exercises
    
    def get_exercise_rank(self, df: pd.DataFrame, exercise_name: str) -> Optional[int]:
        """
        Get the rank of a specific exercise.
        
        Args:
            df: DataFrame with workout data
            exercise_name: Name of the exercise to find
            
        Returns:
            Rank of the exercise (1-based) or None if not found
        """
        frequencies = calculate_exercise_frequency(df)
        
        # Find the exercise in the ranking
        exercise_mask = frequencies['detailed_exercise_name'].str.lower() == exercise_name.lower()
        if exercise_mask.any():
            return frequencies[exercise_mask].index[0] + 1
        
        return None
    
    def get_frequency_distribution(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        Get distribution of exercise frequencies.
        
        Args:
            df: DataFrame with workout data
            
        Returns:
            Dictionary with frequency ranges and counts
        """
        frequencies = calculate_exercise_frequency(df)
        freq_values = frequencies['frequency'].values
        
        distribution = {
            '1-5 times': len(freq_values[(freq_values >= 1) & (freq_values <= 5)]),
            '6-10 times': len(freq_values[(freq_values >= 6) & (freq_values <= 10)]),
            '11-20 times': len(freq_values[(freq_values >= 11) & (freq_values <= 20)]),
            '21+ times': len(freq_values[freq_values >= 21])
        }
        
        return distribution
    
    def analyze_by_timeframe(self, df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        """
        Analyze exercise frequency for a specific timeframe.
        
        Args:
            df: DataFrame with workout data
            timeframe: Timeframe filter (e.g., 'Last 7 days')
            
        Returns:
            DataFrame with frequency data for the specified timeframe
        """
        filtered_df = filter_dataframe_by_timeframe(df, timeframe)
        return calculate_exercise_frequency(filtered_df)


def calculate_exercise_frequency(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate frequency of each exercise in the workout data.
    
    Args:
        df: DataFrame with workout data
        
    Returns:
        DataFrame with exercise frequencies, sorted by frequency descending
    """    
    # Calculate frequencies
    frequencies = df['detailed_exercise_name'].value_counts().reset_index()
    frequencies.columns = ['detailed_exercise_name', 'frequency']
    
    # Sort by frequency descending
    frequencies = frequencies.sort_values('frequency', ascending=False).reset_index(drop=True)
    
    return frequencies


def rank_exercises_by_frequency(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rank exercises by frequency with additional metrics.
    
    Args:
        df: DataFrame with workout data
        
    Returns:
        DataFrame with exercise rankings and metrics
    """
    frequencies = calculate_exercise_frequency(df)
    
    # Add ranking
    frequencies['rank'] = range(1, len(frequencies) + 1)
    
    # Calculate percentage
    total_workouts = frequencies['frequency'].sum()
    frequencies['percentage'] = (frequencies['frequency'] / total_workouts * 100).round(2)
    
    # Reorder columns
    frequencies = frequencies[['rank', 'detailed_exercise_name', 'frequency', 'percentage']]
    
    return frequencies


def calculate_percentage_breakdown(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate percentage breakdown of exercise frequencies.
    
    Args:
        df: DataFrame with workout data
        
    Returns:
        Dictionary mapping exercise names to their percentage of total workouts
    """
    frequencies = calculate_exercise_frequency(df)
    total_workouts = frequencies['frequency'].sum()
    
    percentages = {}
    for _, row in frequencies.iterrows():
        exercise_name = row['detailed_exercise_name']
        frequency = row['frequency']
        percentage = (frequency / total_workouts * 100)
        percentages[exercise_name] = round(percentage, 2)
    
    return percentages


def get_frequency_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get summary statistics for workout frequency.
    
    Args:
        df: DataFrame with workout data
        
    Returns:
        Dictionary with frequency summary statistics
    """
    frequencies = calculate_exercise_frequency(df)
    
    summary = {
        'total_exercises': len(frequencies),
        'total_workouts': frequencies['frequency'].sum(),
        'most_frequent_exercise': frequencies.iloc[0]['detailed_exercise_name'],
        'most_frequent_count': frequencies.iloc[0]['frequency'],
        'average_frequency': round(frequencies['frequency'].mean(), 2),
        'median_frequency': round(frequencies['frequency'].median(), 2),
        'min_frequency': frequencies['frequency'].min(),
        'max_frequency': frequencies['frequency'].max()
    }
    
    return summary


def analyze_all_exercises(df: pd.DataFrame, key_metric: str, timeframe: str = 'All time') -> pd.DataFrame:
    """
    Analyze all exercises by key metric and timeframe.
    
    Args:
        df: DataFrame with workout data
        key_metric: Key metric to analyze ('Max Volume', 'Max Weight', 'Average Reps', 'Count')
        timeframe: Timeframe filter
        
    Returns:
        DataFrame with exercise analysis results
    """
    # Validate key metric
    valid_metrics = ['Max Volume', 'Max Weight', 'Average Reps', 'Count']
    if key_metric not in valid_metrics:
        raise ValueError(f"Invalid key metric. Must be one of: {valid_metrics}")
    
    # Filter by timeframe if needed
    df = filter_dataframe_by_timeframe(df, timeframe)
    
    # Calculate metrics based on key metric
    if key_metric == 'Count':
        result = df['detailed_exercise_name'].value_counts().reset_index()
        result.columns = ['detailed_exercise_name', 'count']
        result = result.sort_values('count', ascending=False)
    
    elif key_metric == 'Max Weight':
        result = df.groupby('detailed_exercise_name')['weight'].max().reset_index()
        result.columns = ['detailed_exercise_name', 'max_weight']
        result = result.sort_values('max_weight', ascending=False)
    
    elif key_metric == 'Average Reps':
        result = df.groupby('detailed_exercise_name')['reps'].mean().reset_index()
        result.columns = ['detailed_exercise_name', 'avg_reps']
        result['avg_reps'] = result['avg_reps'].round(2)
        result = result.sort_values('avg_reps', ascending=False)
    
    elif key_metric == 'Max Volume':
        # Calculate volume: weight * sets * reps (divide by 2 for alternating exercises)
        df_copy = df.copy()
        df_copy['volume'] = df_copy['weight'] * df_copy['sets'] * df_copy['reps']
        
        alternating_mask = df_copy['alternating'] == True
        df_copy.loc[alternating_mask, 'volume'] = df_copy.loc[alternating_mask, 'volume'] * 2
        
        result = df_copy.groupby('detailed_exercise_name')['volume'].max().reset_index()
        result.columns = ['detailed_exercise_name', 'max_volume']
        result = result.sort_values('max_volume', ascending=False)
    
    # Add ranking
    result['rank'] = range(1, len(result) + 1)
    
    # Reorder columns
    result = result[['rank', 'detailed_exercise_name', result.columns[1]]]
    
    return result

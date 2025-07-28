# DataFrame Structure and Data Flow

## Data Schema Overview

This document describes the dataframe structure used throughout the Exercise Mobile App project, including the data extraction, transformation, and analysis pipeline.

## DataFrame Schema Diagram

```mermaid
erDiagram
    WORKOUT_DATA {
        datetime workout_date
        string detailed_exercise_name
        float weight
        int sets
        int reps
        boolean alternating
        float volume
    }

    RAW_GOOGLE_SHEETS {
        string WorkoutDate
        string ExerciseType
        string ExerciseName
        string Weight
        string Sets
        string DiscreteReps
        string Alternating
    }

    VALIDATION_RULES {
        string WorkoutDate
        string ExerciseType
        string ExerciseName
        string Weight
        string Sets
        string DiscreteReps
    }

    RAW_GOOGLE_SHEETS ||--|| WORKOUT_DATA : "Column Mapping"
    RAW_GOOGLE_SHEETS ||--|| VALIDATION_RULES : "Enforced By"
```

## Data Flow Pipeline

```mermaid
flowchart TD
    A[Google Sheets Source] --> B[GoogleSheetsExtractor]
    B --> C[Raw DataFrame]
    C --> D[WorkoutDataValidator]
    D --> E[Validated DataFrame]
    E --> F[Data Analysis Modules]
    
    F --> G[Overview Statistics]
    F --> H[Workout Statistics]
    F --> I[All Exercise Statistics]
    F --> J[Specific Exercise Analysis]
    
    G --> K[Frontend Dashboard]
    H --> K
    I --> K
    J --> K
    
    subgraph "Data Extraction"
        A
        B
        C
    end
    
    subgraph "Data Validation"
        D
        E
    end
    
    subgraph "Data Analysis"
        F
        G
        H
        I
        J
    end
    
    subgraph "Frontend"
        K
    end
```

## Column Mapping and Transformation

```mermaid
graph LR
    subgraph "Google Sheets"
        A1["Workout Date"]
        A2["Exercise Type"]
        A3["Exercise Name"]
        A4["Weight"]
        A5["Sets"]
        A6["Discrete Reps"]
        A7["Alternating"]
    end
    
    subgraph "Target Schema"
        B1["workout_date<br/>datetime64[ns]"]
        B2["detailed_exercise_name<br/>string"]
        B4["weight<br/>float64"]
        B5["sets<br/>int64"]
        B6["reps<br/>int64"]
        B7["alternating<br/>boolean"]
        B8["volume<br/>float64"]
    end
    
    A1 --> B1
    A2 --> B2
    A3 --> B2
    A4 --> B4
    A5 --> B5
    A6 --> B6
    A7 --> B7
    B4 --> B8
    B5 --> B8
    B6 --> B8
```

## ETL Process

```mermaid
flowchart TD
    subgraph "Extraction"
        Z[Google Sheets] --> A[Raw Data]
    end

    subgraph "Validation"
        A --> B{Required Fields Present?}
        B -->|No| C[Error: Missing Columns]
        B -->|Yes| D[Rename Fields]
        
        D --> E{Data Types Coercable?}
        E -->|No| F[Error: Invalid Types]
        E -->|Yes| G[Update Data Types]

        G --> H{Constraints Met?}
        H -->|No| I[Error: Invalid Values]
    end
    
    subgraph "Transformation"
    H -->|Yes| M[Derive Fields]
    
    M --> N[Final Transformed DataFrame]
    end
    
    C --> O[Validation Result]
    F --> O
    I --> O
    N --> O
```

## Key Features and Analytics

```mermaid
mindmap
  root((Workout Data<br/>Analytics))
    Weight Progress
      Max Weight Tracking
      Weight Progression Charts
      Exercise-Specific Trends
    Workout Frequency
      Rolling 30-Day Count
      Workout Consistency
      Time-Based Analysis
    Exercise Analysis
      Most Frequent Exercises
      Exercise Performance
      Volume Calculations
    Summary Statistics
      Overall Progress
      Key Performance Indicators
      Comparative Analysis
```

## Data Relationships and Dependencies

```mermaid
graph TD
    A[workout_date] --> B[Time-based Analysis]
    A --> C[Progress Tracking]
    
    D[exercise_name] --> E[Exercise-Specific Views]
    D --> F[Frequency Analysis]
    
    G[weight_lbs] --> H[Strength Progress]
    G --> I[Volume Calculations]
    
    J[sets] --> I
    K[discrete_reps] --> I
    
    L[exercise_type] --> M[Category Analysis]
    
    N[alternating] --> O[Exercise Variation Tracking]
    
```

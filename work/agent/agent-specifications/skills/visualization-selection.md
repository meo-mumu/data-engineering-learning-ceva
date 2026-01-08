# Visualization Selection Skill

## Overview

Choose the appropriate visualization type based on data characteristics and user question intent.

## Selection Rules

Choose the appropriate visualization based on data patterns:

| Data Pattern | View Type | When to Use |
|--------------|-----------|-------------|
| Single metric, no grouping | **Table** | One value or simple scalar result |
| List of records | **Table** | Multiple rows with few columns (<10 columns) |
| Trend over time | **Line chart** | Time series data, showing evolution |
| Comparison across categories | **Bar chart** | Comparing metrics across groups (e.g., by BU, by site) |
| Part-to-whole relationship | **Pie chart** | Distribution/proportion (≤7 categories only) |
| Correlation between 2 metrics | **Scatter plot** | Relationship between two numerical variables |

**Default:** When in doubt, use **table** view.

## Detailed Selection Logic

### TABLE VIEW
**When to Use:**
- Single scalar result (1 row, 1-2 columns)
- Many columns (>6 columns) where chart would be cluttered
- Mixed data types that don't support meaningful charting
- Small result sets (<10 rows) with diverse information

### BAR CHART
**When to Use:**
- Comparing discrete categories (business units, products, sites)
- Aggregated metrics (counts, sums, averages) by category
- 2-5 columns: 1 categorical, 1-4 numeric metrics
- Reasonable number of categories (<30 for readability)

### LINE CHART (Time Series)
**When to Use:**
- Time-based data (date, month, year, quarter columns)
- Showing trends, patterns, seasonality over time
- Continuous time series or periodic measurements

**Column Detection Heuristics:**
- Column names containing: "date", "time", "month", "year", "quarter", "period", "week"
- Column with datetime type or ISO date format strings

### PIE CHART (Distribution)
**When to Use:**
- Part-to-whole relationships (proportions, percentages)
- Small number of categories (≤7 for readability)
- 2 columns: 1 categorical (names), 1 numeric (values)
- When showing composition matters more than exact values

**Avoid When:**
- Many categories (>7) - use bar chart instead
- Comparing multiple metrics - use bar chart
- Showing trends - use line chart

### SCATTER PLOT
**When to Use:**
- Exploring correlation between two numeric variables
- Identifying patterns, clusters, outliers
- 2-3 columns: 2 numeric (x, y), optional 1 categorical (color)

## Analysis Process

When selecting visualization:
1. Analyze the data characteristics (row count, column types, value distributions)
2. Consider the user's original question intent
3. Select the most appropriate visualization type
4. Generate complete, executable code for the `render_visualization()` function

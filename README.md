# CEVA Animal Health - Data stack lakehouse POC

The project is in @work.

## Data sources [DONE]

Source data in:
- @work/data/a-sources/bu_companion_catalog.json
- @work/data/a-sources/bu_poultry_production.csv
- @work/data/a-sources/bu_ruminants_production.csv

Data description in @work/data/a-sources/data-description.md

## ETL [DONE]

ETL scripts are in @work/scripts/etl.py
We use Python to create the silver layers. [TODO for silver data vault]

## Silver

2 parallel architectures:
- data vault in @work/data/b-silver-data-vault/ [TODO]
- star schema in @work/data/b-silver-star-schema/ [DONE]

Since we're building a data lakehouse, we store in **parquet** format.

## Script de test [DONE]
Contient un notebook avec une cellule qui affiche les données des tables du star schema, à partir d'une requete sql.
dans @work/scripts/ 

## Semantic layer [DONE]
The semantic layer is a simple @work/data/semantic_layer.yaml file that will be read by a dedicated agent.
Additionally there will be question/answer examples.

## Agent [TODO]

### Role

Data analyst agent specialized in translating natural language questions into SQL queries for DuckDB. Analyse user intent, generate optimized SQL, select appropriate visualizations, and produce Streamlit code.

### Capabilities

1. **Natural Language to SQL**: Convert user questions into valid DuckDB SQL queries
2. **Visualization Selection**: Choose the best view type (table, bar chart, line chart, pie chart, scatter plot)
3. **Streamlit Code Generation**: Output ready-to-run Streamlit code using provided templates

### SQL Guidelines

#### DuckDB Specifics
- Use `STRFTIME('%Y-%m', date_col)` for month grouping
- Use `DATE_TRUNC('month', date_col)` for date truncation
- Use `ILIKE` for case-insensitive pattern matching
- Use `LIMIT` to cap results (default: 1000 rows)
- Prefer CTEs over nested subqueries for readability

#### Query Safety
- Generate **SELECT statements only** — never INSERT, UPDATE, DELETE, DROP
- Always include a `LIMIT` clause (max 10000)
- Avoid `SELECT *` — explicitly list required columns

#### Star Schema Navigation
- Identify the relevant fact table based on the metric requested
- Join dimension tables only when filtering or grouping by their attributes

### Visualization Selection Rules

| Data Pattern | Recommended View |
|--------------|------------------|
| Single metric, no grouping | Table (single value) |
| List of records | Table |
| Trend over time | Line chart |
| Comparison across categories | Bar chart |
| Part-to-whole relationship | Pie chart (≤7 categories) |
| Correlation between 2 metrics | Scatter plot |

When in doubt, default to **table**.


### Agent technology Stack
LangGraph with HuggingFaceHub integration for agent  
code in @work/agent/agent.py   

## Environment

Python env with **uv** (pyproject.toml)
git : https://github.com/meo-mumu/data-engineering-learning-ceva.git
# SQL Generation Skill

## Overview

Generate optimized DuckDB SQL queries from natural language questions using the semantic layer.

## Data Sources

**Semantic Layer:** `work/data/semantic_layer.yaml`
- Contains the complete star schema definition (tables, columns, types, relationships)
- Includes question/answer examples demonstrating query patterns

**Parquet Files:** `work/data/b-silver-star-schema/`
- `dim_product.parquet` - Product catalog across all business units
- `dim_specie.parquet` - Target animal species dimension
- `dim_site.parquet` - Production site dimension
- `fact_batch_production.parquet` - Batch production fact table (grain: one row per batch/lot)

## DuckDB Specifics

- Use `STRFTIME('%Y-%m', date_col)` for month grouping
- Use `DATE_TRUNC('month', date_col)` for date truncation
- Use `ILIKE` for case-insensitive pattern matching
- Use `LIMIT` to cap results (default: 1000 rows, max: 10000)
- Prefer CTEs (Common Table Expressions) over nested subqueries for readability
- Tables are accessed via pre-created views (no need for `read_parquet()`)

## Query Safety Rules (ENFORCE STRICTLY)

- Generate **SELECT statements ONLY** - NEVER use INSERT, UPDATE, DELETE, DROP, CREATE, ALTER, TRUNCATE
- **ALWAYS include a LIMIT clause** (default: 1000, maximum: 10000)
- **Avoid SELECT \*** - Explicitly list only required columns
- No DDL or DML operations allowed
- Read-only access to data

## Star Schema Navigation

- **Identify the relevant fact table** based on the metric requested (typically `fact_batch_production`)
- **Join dimension tables** only when filtering or grouping by their attributes
- Use **LEFT JOIN** for dimensions that may be NULL (e.g., `dim_site` for companion animal batches)
- Leverage **surrogate keys** (SK) and **foreign keys** (FK) for joins
- Use **UNNEST** for array-type columns (e.g., `targeted_species` in fact table)

## Query Optimization

- Filter early in the query (use WHERE clauses before joins when possible)
- Aggregate at the appropriate grain
- Use explicit column names for clarity
- Add ORDER BY for consistent result ordering

## Quality Standards

- **Correctness:** SQL must be syntactically valid DuckDB
- **Safety:** Strictly enforce read-only operations
- **Performance:** Include LIMIT clauses, avoid unnecessary joins
- **Clarity:** Use meaningful aliases, proper formatting
- **Completeness:** Answer the full question, not a partial subset

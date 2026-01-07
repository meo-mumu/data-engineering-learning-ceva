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

## Agent [IN PROGRESS]
Data analyst agent specialized in translating natural language questions into SQL queries for DuckDB. Analyse user intent, generate optimized SQL, select appropriate visualizations, and produce Streamlit code.

The agent specifications, roles, capabilities, and guidelines are in @work/agent/agent-specifications.md.
The agent code is in @work/agent/agent.py
Techno : LangGraph with HuggingFaceHub integration for agent  

## RAG [TODO]

## Streamlit app [DONE]
The Streamlit app will be in @work/streamlit-app/streamlit_app.py
The app is a template with features:
- at the top a text input for user questions
- below the text input, an area to display the generated SQL query
- below the SQL query area, a visualization area to display charts or tables based on the agent's output.

## Environment

Python env with **uv** (pyproject.toml)
git : https://github.com/meo-mumu/data-engineering-learning-ceva.git
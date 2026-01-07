"""SQL execution node - runs queries against DuckDB"""

import duckdb
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..agent import AgentState


def execute_sql(state: "AgentState") -> "AgentState":
    """Execute SQL query against DuckDB"""
    print("🔍 Executing SQL...")

    sql = state.get("generated_sql", "").strip()

    if not sql:
        print("❌ No SQL to execute")
        state["query_results"] = []
        state["result_columns"] = []
        return state

    try:
        # Create in-memory DuckDB connection
        conn = duckdb.connect(":memory:")

        # Execute the query
        result = conn.execute(sql)

        # Fetch all results as list of tuples
        rows = result.fetchall()

        # Get column names
        columns = [desc[0] for desc in result.description]

        # Store in state
        state["query_results"] = rows
        state["result_columns"] = columns

        # Close connection
        conn.close()

        print(f"✅ Executed successfully: {len(rows)} rows, {len(columns)} columns")

    except Exception as e:
        print(f"❌ SQL execution failed: {str(e)}")
        state["query_results"] = []
        state["result_columns"] = []
        # Optionally store error for debugging
        state["validation_error"] = f"SQL execution error: {str(e)}"

    return state

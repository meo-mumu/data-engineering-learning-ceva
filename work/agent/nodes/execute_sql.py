"""SQL execution node - runs queries against DuckDB"""

import duckdb
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..agent import AgentState


def create_execute_sql_node(conn: duckdb.DuckDBPyConnection):
    """Factory function to create execute_sql node with persistent DuckDB connection"""

    def execute_sql(state: "AgentState") -> "AgentState":
        """Execute SQL query against DuckDB using persistent connection"""
        print("🔍 Executing SQL...")

        sql = state.get("generated_sql", "").strip()

        if not sql:
            print("❌ No SQL to execute")
            state["query_results"] = []
            state["result_columns"] = []
            return state

        try:
            # Execute the query using persistent connection with views
            result = conn.execute(sql)

            # Fetch all results as list of tuples
            rows = result.fetchall()

            # Get column names
            columns = [desc[0] for desc in result.description]

            # Store in state
            state["query_results"] = rows
            state["result_columns"] = columns

            print(f"✅ Executed successfully: {len(rows)} rows, {len(columns)} columns")

        except Exception as e:
            print(f"❌ SQL execution failed: {str(e)}")
            state["execution_error"] = True
            state["query_results"] = []
            state["result_columns"] = []
            # Store error message for user display
            state["validation_error"] = f"SQL execution error: {str(e)}"

        return state

    return execute_sql

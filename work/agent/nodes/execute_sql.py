"""SQL execution node - runs queries against DuckDB"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..agent import AgentState


def execute_sql(state: "AgentState") -> "AgentState":
    """Execute SQL query against DuckDB"""
    print("🔍 Executing SQL...")
    # TODO: Implement SQL execution
    return state

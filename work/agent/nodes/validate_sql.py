"""SQL validation node - ensures generated SQL is safe and correct"""

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..agent import AgentState


# Forbidden SQL keywords (DDL/DML operations)
FORBIDDEN_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER",
    "TRUNCATE", "REPLACE", "MERGE", "GRANT", "REVOKE"
]

# Maximum allowed LIMIT value
MAX_LIMIT = 10000


def validate_sql(state: "AgentState") -> "AgentState":
    """Validate generated SQL for safety and correctness"""
    print("✅ Validating SQL...")

    sql = state.get("generated_sql", "").strip()

    if not sql:
        state["sql_valid"] = False
        state["validation_error"] = "No SQL query generated"
        print(f"❌ Validation failed: {state['validation_error']}")
        return state

    # Normalize SQL for checking (uppercase, remove extra whitespace)
    sql_upper = " ".join(sql.upper().split())

    # Check 1: Must be SELECT only
    if not sql_upper.startswith("SELECT") and not sql_upper.startswith("WITH"):
        state["sql_valid"] = False
        state["validation_error"] = "Query must be a SELECT statement (or CTE starting with WITH)"
        print(f"❌ Validation failed: {state['validation_error']}")
        return state

    # Check 2: No forbidden keywords (DDL/DML operations)
    for keyword in FORBIDDEN_KEYWORDS:
        # Use word boundaries to avoid false positives (e.g., "INSERTED" column name)
        pattern = r'\b' + keyword + r'\b'
        if re.search(pattern, sql_upper):
            state["sql_valid"] = False
            state["validation_error"] = f"Forbidden operation detected: {keyword}. Only SELECT queries allowed."
            print(f"❌ Validation failed: {state['validation_error']}")
            return state

    # Check 3: Must have LIMIT clause
    if not re.search(r'\bLIMIT\s+\d+', sql_upper):
        state["sql_valid"] = False
        state["validation_error"] = "Query must include a LIMIT clause (max 10000)"
        print(f"❌ Validation failed: {state['validation_error']}")
        return state

    # Check 4: LIMIT value must be <= MAX_LIMIT
    limit_match = re.search(r'\bLIMIT\s+(\d+)', sql_upper)
    if limit_match:
        limit_value = int(limit_match.group(1))
        if limit_value > MAX_LIMIT:
            state["sql_valid"] = False
            state["validation_error"] = f"LIMIT value ({limit_value}) exceeds maximum allowed ({MAX_LIMIT})"
            print(f"❌ Validation failed: {state['validation_error']}")
            return state

    # Check 5: Warn about SELECT * (not blocking, just a warning)
    if re.search(r'\bSELECT\s+\*\b', sql_upper):
        print("⚠️  Warning: Query uses SELECT * - consider specifying explicit columns")

    # All checks passed
    state["sql_valid"] = True
    state["validation_error"] = ""
    print("✅ Validation passed")

    return state

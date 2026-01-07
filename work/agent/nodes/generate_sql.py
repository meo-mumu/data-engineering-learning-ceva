"""SQL generation node - converts natural language to DuckDB SQL"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..agent import AgentState


def create_generate_sql_node(llm, agent_specs: str, semantic_layer: str):
    """Factory function to create generate_sql node with dependencies"""

    def generate_sql(state: "AgentState") -> "AgentState":
        """Generate SQL query from natural language question"""

        # Check if this is a retry due to validation failure
        validation_error = state.get("validation_error", "")
        previous_sql = state.get("generated_sql", "")

        if validation_error and previous_sql:
            # Increment retry count
            state["retry_count"] = state.get("retry_count", 0) + 1
            print(f"🔄 Regenerating SQL (attempt {state['retry_count']}/3, fixing: {validation_error})...")
        else:
            print("🔄 Generating SQL...")

        # Build prompt with validation feedback if retrying
        error_feedback = ""
        if validation_error and previous_sql:
            error_feedback = f"""

---

# PREVIOUS ATTEMPT FAILED

Your previous SQL query had this error:
**{validation_error}**

Previous SQL:
```sql
{previous_sql}
```

Please fix this error and generate a corrected SQL query.
"""

        # Build simple prompt - let LLM understand the YAML directly
        prompt = f"""{agent_specs}

---

# SEMANTIC LAYER

{semantic_layer}

---

# USER QUESTION

{state["question"]}
{error_feedback}

---

Generate ONLY the SQL query needed to answer this question. Return the SQL without any explanation or markdown formatting.
"""

        # Call LLM with timeout handling
        try:
            response = llm.invoke(prompt)
            generated_text = response.content.strip()
        except TimeoutError as e:
            print(f"⏱️  LLM timeout: {e}")
            state["validation_error"] = "LLM timeout, please retry"
            state["generated_sql"] = ""
            state["sql_valid"] = False
            return state
        except Exception as e:
            # Catch other exceptions (network errors, API errors, etc.)
            error_msg = str(e)
            if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                print(f"⏱️  LLM timeout (caught as general exception): {e}")
                state["validation_error"] = "LLM timeout, please retry"
            else:
                print(f"❌ LLM invocation failed: {e}")
                state["validation_error"] = f"LLM error: {error_msg}"
            state["generated_sql"] = ""
            state["sql_valid"] = False
            return state

        # Extract SQL (remove markdown formatting if present)
        sql = generated_text
        if "```sql" in sql:
            sql = sql.split("```sql")[1].split("```")[0].strip()
        elif "```" in sql:
            sql = sql.split("```")[1].split("```")[0].strip()

        state["generated_sql"] = sql
        print(f"📝 Generated SQL:\n{sql}\n")

        return state

    return generate_sql

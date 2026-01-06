"""SQL generation node - converts natural language to DuckDB SQL"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..agent import AgentState


def create_generate_sql_node(llm, agent_specs: str, semantic_layer: str):
    """Factory function to create generate_sql node with dependencies"""

    def generate_sql(state: "AgentState") -> "AgentState":
        """Generate SQL query from natural language question"""
        print("🔄 Generating SQL...")

        # Build simple prompt - let LLM understand the YAML directly
        prompt = f"""{agent_specs}

---

# SEMANTIC LAYER

{semantic_layer}

---

# USER QUESTION

{state["question"]}

---

Generate ONLY the SQL query needed to answer this question. Return the SQL without any explanation or markdown formatting.
"""

        # Call LLM
        response = llm.invoke(prompt)
        generated_text = response.content.strip()

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

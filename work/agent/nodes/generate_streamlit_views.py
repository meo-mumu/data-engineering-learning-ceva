"""Generate Streamlit views - LLM-driven visualization code generation"""

import re
import ast
from pathlib import Path
from typing import TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from ..agent import AgentState


# Path to streamlit app
STREAMLIT_APP_PATH = Path(__file__).parent.parent.parent / "streamlit-app" / "streamlit_app.py"
START_MARKER = "# START AGENT GENERATED CODE"
END_MARKER = "# END AGENT GENERATED CODE"

# Safety validation constants
ALLOWED_IMPORTS = {'pandas', 'pd', 'streamlit', 'st', 'plotly', 'plotly.express', 'px'}
FORBIDDEN_IMPORTS = {'os', 'sys', 'subprocess', 'eval', 'exec', '__import__', 'open', 'file', 'input', 'requests', 'urllib', 'socket', 'http'}
FORBIDDEN_FUNCTIONS = ['eval', 'exec', '__import__', 'compile', 'open', 'file', 'input', 'raw_input', 'getattr', 'setattr', 'delattr']


def analyze_data_context(rows: list, columns: list, question: str, sql: str) -> dict:
    """Prepare structured metadata for LLM prompt

    Returns:
        {
            "num_rows": int,
            "num_columns": int,
            "column_metadata": [
                {"name": str, "inferred_type": str, "sample_values": list, "has_nulls": bool}
            ],
            "data_sample": list[dict],
            "sql_context": str,
            "question_context": str
        }
    """
    num_rows = len(rows)
    num_columns = len(columns)

    # Analyze each column
    column_metadata = []
    for col_idx, col_name in enumerate(columns):
        # Extract column values (up to first 10 rows for type inference)
        col_values = [row[col_idx] if col_idx < len(row) else None for row in rows[:10]]

        # Infer type
        inferred_type = infer_column_type(col_values)

        # Sample diverse values (first 5 non-null)
        sample_values = [v for v in col_values if v is not None][:5]

        # Check for nulls
        has_nulls = any(row[col_idx] is None if col_idx < len(row) else True for row in rows)

        column_metadata.append({
            "name": col_name,
            "inferred_type": inferred_type,
            "sample_values": sample_values,
            "has_nulls": has_nulls
        })

    # Sample first 3 rows as dicts
    data_sample = []
    for row in rows[:3]:
        row_dict = {columns[i]: row[i] if i < len(row) else None for i in range(len(columns))}
        data_sample.append(row_dict)

    return {
        "num_rows": num_rows,
        "num_columns": num_columns,
        "column_metadata": column_metadata,
        "data_sample": data_sample,
        "sql_context": sql,
        "question_context": question
    }


def infer_column_type(values: list) -> str:
    """Infer column type from sample values"""
    # Filter out None values
    non_null_values = [v for v in values if v is not None]

    if not non_null_values:
        return "unknown"

    # Check if all are numeric
    if all(isinstance(v, (int, float)) for v in non_null_values):
        return "numeric"

    # Check if any look like dates (ISO format or datetime objects)
    if any(isinstance(v, datetime) for v in non_null_values):
        return "datetime"

    # Check string dates (ISO format: YYYY-MM-DD)
    if all(isinstance(v, str) for v in non_null_values):
        # Simple check for date patterns
        if any(re.match(r'\d{4}-\d{2}-\d{2}', str(v)) for v in non_null_values[:3]):
            return "datetime"

    # Default to string/categorical
    return "string"


def build_visualization_prompt(context: dict, viz_guidelines: str) -> str:
    """Construct LLM prompt with guidelines + data context"""

    # Format column metadata
    column_details = []
    for col in context['column_metadata']:
        column_details.append(f"- **{col['name']}**: {col['inferred_type']}")
        column_details.append(f"  - Sample values: {col['sample_values']}")
        column_details.append(f"  - Has nulls: {col['has_nulls']}")
    column_details_str = "\n".join(column_details)

    # Format sample data
    sample_data_str = "\n".join([str(row) for row in context['data_sample']])

    prompt = f"""# ROLE
You are a data visualization expert generating Plotly code for Streamlit applications.

# TASK
Generate a complete Python function `render_visualization()` that creates the most appropriate
visualization for the given data and user question.

{viz_guidelines}

---

# DATA CONTEXT

## Original Question
{context['question_context']}

## SQL Query Used
```sql
{context['sql_context']}
```

## Result Metadata
- Rows: {context['num_rows']}
- Columns: {context['num_columns']}

## Column Details
{column_details_str}

## Sample Data (First 3 rows)
{sample_data_str}

---

# OUTPUT REQUIREMENTS

Generate ONLY the complete Python function code following the guidelines above.
The code will be directly injected into a Streamlit app - it must be immediately executable.

Do NOT include:
- Explanatory text or reasoning
- Multiple options or alternatives
- Comments outside the code

Begin your response with the function definition.
"""

    return prompt


def extract_python_code(llm_response: str) -> str:
    """Parse LLM response to extract clean Python code"""
    response = llm_response.strip()

    # Check for ```python code blocks
    if "```python" in response:
        code = response.split("```python")[1].split("```")[0].strip()
        return code

    # Check for generic ``` blocks
    if "```" in response:
        code = response.split("```")[1].split("```")[0].strip()
        return code

    # Assume entire response is code
    return response


def validate_generated_code(code: str) -> tuple[bool, str]:
    """Multi-layer validation for LLM-generated code

    Returns:
        (is_valid: bool, error_message: str)
    """
    # Layer 1: Syntax validation
    try:
        compile(code, '<string>', 'exec')
    except SyntaxError as e:
        return False, f"Syntax error: {e}"

    # Layer 2-4: AST-based validation
    try:
        tree = ast.parse(code)
    except Exception as e:
        return False, f"AST parsing failed: {e}"

    # Layer 2: Import whitelist
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name.split('.')[0]  # Get base module
                if module not in ALLOWED_IMPORTS:
                    return False, f"Forbidden import: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                module = node.module.split('.')[0]
                if module not in ALLOWED_IMPORTS:
                    return False, f"Forbidden import from: {node.module}"

    # Layer 3: Forbidden function calls
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in FORBIDDEN_FUNCTIONS:
                    return False, f"Forbidden function call: {node.func.id}"

    # Layer 4: Function signature validation
    has_correct_signature = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name == 'render_visualization':
                args = [arg.arg for arg in node.args.args]
                if args == ['viz_type', 'columns', 'rows']:
                    has_correct_signature = True
                    break

    if not has_correct_signature:
        return False, "Missing or incorrect render_visualization signature"

    return True, ""


def generate_safe_table_fallback(columns: list) -> str:
    """Generate safe table view when LLM fails validation"""
    return '''def render_visualization(viz_type: str, columns: list, rows: list):
    """Render visualization - SAFE FALLBACK"""
    import pandas as pd
    import streamlit as st

    df = pd.DataFrame(rows, columns=columns)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"Showing {len(df)} rows × {len(df.columns)} columns")
'''


def update_streamlit_app(generated_code: str):
    """Update streamlit_app.py with generated visualization code"""

    # Read current file
    with open(STREAMLIT_APP_PATH, "r") as f:
        content = f.read()

    # Find markers
    pattern = re.compile(
        f"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}",
        re.DOTALL
    )

    # Replace code between markers
    new_content = pattern.sub(
        f"{START_MARKER}\n{generated_code}{END_MARKER}",
        content
    )

    # Write back
    with open(STREAMLIT_APP_PATH, "w") as f:
        f.write(new_content)


def create_generate_streamlit_views_node(llm, viz_guidelines: str):
    """Factory function to inject LLM and guidelines dependencies"""

    def generate_streamlit_views(state: "AgentState") -> "AgentState":
        """Generate Streamlit visualization code using LLM"""
        print("🎨 Generating Streamlit views...")

        # 1. Extract state
        rows = state.get("query_results", [])
        columns = state.get("result_columns", [])
        question = state.get("question", "")
        sql = state.get("generated_sql", "")

        # 2. Analyze data context
        context = analyze_data_context(rows, columns, question, sql)
        print(f"→ Data: {context['num_rows']} rows, {context['num_columns']} columns")

        # 3. Build LLM prompt
        prompt = build_visualization_prompt(context, viz_guidelines)

        # 4. Call LLM
        try:
            response = llm.invoke(prompt)
            generated_code = extract_python_code(response.content)
        except Exception as e:
            print(f"❌ LLM invocation failed: {e}")
            generated_code = generate_safe_table_fallback(columns)
            state["streamlit_code"] = generated_code
            update_streamlit_app(generated_code)
            return state

        # 5. Validate generated code
        is_valid, error = validate_generated_code(generated_code)

        if not is_valid:
            # Fallback to safe table view
            generated_code = generate_safe_table_fallback(columns)
            print(f"⚠️  Validation failed: {error}. Using table fallback.")
        else:
            print("✅ Generated code validated")

        # 6. Update streamlit app file
        try:
            update_streamlit_app(generated_code)
            print(f"✅ Updated {STREAMLIT_APP_PATH}")
        except Exception as e:
            print(f"❌ Failed to update streamlit app: {e}")

        # 7. Store in state
        state["streamlit_code"] = generated_code

        return state

    return generate_streamlit_views

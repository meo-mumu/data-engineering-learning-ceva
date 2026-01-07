"""Generate Streamlit views - LLM-driven visualization code generation"""

import re
import ast
from typing import TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from ..agent import AgentState

# Safety validation constants
ALLOWED_IMPORTS = {'pandas', 'pd', 'streamlit', 'st', 'plotly', 'plotly.express', 'px'}
FORBIDDEN_IMPORTS = {'os', 'sys', 'subprocess', 'eval', 'exec', '__import__', 'open', 'file', 'input', 'requests', 'urllib', 'socket', 'http'}
FORBIDDEN_FUNCTIONS = ['eval', 'exec', '__import__', 'compile', 'open', 'file', 'input', 'raw_input', 'getattr', 'setattr', 'delattr']

# Forbidden module.method patterns (for ast.Attribute calls)
FORBIDDEN_METHODS = {
    'os': ['system', 'popen', 'execl', 'execle', 'execlp', 'execlpe', 'execv', 'execve',
           'execvp', 'execvpe', 'spawnl', 'spawnle', 'spawnlp', 'spawnlpe', 'spawnv',
           'spawnve', 'spawnvp', 'spawnvpe'],
    'subprocess': '*',  # Block all subprocess methods
    'builtins': ['__import__', 'eval', 'exec', 'compile'],
}


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

    Test Cases - These patterns should be BLOCKED:
    ✗ eval('malicious_code')                  # Direct forbidden function
    ✗ exec('malicious_code')                  # Direct forbidden function
    ✗ __import__('os')                        # Direct forbidden function
    ✗ open('/etc/passwd')                     # Direct forbidden function
    ✗ os.system('rm -rf /')                   # Module method call
    ✗ os.popen('cat /etc/passwd')             # Module method call
    ✗ os.execv('/bin/sh', [])                 # Module method call
    ✗ subprocess.run(['rm', '-rf', '/'])      # All subprocess methods blocked
    ✗ subprocess.Popen(['malicious'])         # All subprocess methods blocked
    ✗ subprocess.call(['cmd'])                # All subprocess methods blocked
    ✗ builtins.__import__('os')               # Module method call
    ✓ pd.DataFrame(rows, columns=columns)     # Allowed (pandas)
    ✓ st.plotly_chart(fig)                    # Allowed (streamlit)
    ✓ px.bar(df, x='col1', y='col2')          # Allowed (plotly)

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
            # Check direct function calls (e.g., eval(), exec())
            if isinstance(node.func, ast.Name):
                if node.func.id in FORBIDDEN_FUNCTIONS:
                    return False, f"Forbidden function call: {node.func.id}"

            # Check method calls (e.g., os.system(), subprocess.run())
            elif isinstance(node.func, ast.Attribute):
                # Get the module/object name (e.g., "os" from os.system)
                if isinstance(node.func.value, ast.Name):
                    module_name = node.func.value.id
                    method_name = node.func.attr

                    # Check if module is in forbidden list
                    if module_name in FORBIDDEN_METHODS:
                        forbidden_list = FORBIDDEN_METHODS[module_name]
                        # If '*', block all methods from this module
                        if forbidden_list == '*':
                            return False, f"Forbidden method call: {module_name}.{method_name}"
                        # Otherwise check specific method names
                        elif method_name in forbidden_list:
                            return False, f"Forbidden method call: {module_name}.{method_name}"

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

        # 4. Call LLM with timeout handling
        try:
            response = llm.invoke(prompt)
            generated_code = extract_python_code(response.content)
        except TimeoutError as e:
            print(f"⏱️  LLM timeout: {e}. Using safe table fallback.")
            generated_code = generate_safe_table_fallback(columns)
            state["streamlit_code"] = generated_code
            return state
        except Exception as e:
            error_msg = str(e)
            if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                print(f"⏱️  LLM timeout (caught as general exception): {e}. Using safe table fallback.")
            else:
                print(f"❌ LLM invocation failed: {e}. Using safe table fallback.")
            generated_code = generate_safe_table_fallback(columns)
            state["streamlit_code"] = generated_code
            return state

        # 5. Validate generated code
        is_valid, error = validate_generated_code(generated_code)

        if not is_valid:
            # Fallback to safe table view
            generated_code = generate_safe_table_fallback(columns)
            print(f"⚠️  Validation failed: {error}. Using table fallback.")
        else:
            print("✅ Generated code validated")

        # 6. Store in state (no file writing - Streamlit will execute dynamically)
        state["streamlit_code"] = generated_code

        return state

    return generate_streamlit_views

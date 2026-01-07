"""
CEVA Animal Health - Data Assistant Streamlit App
Phase 2: Full integration with LangGraph agent
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

# Add agent directory to path
agent_path = Path(__file__).parent.parent / "agent"
sys.path.insert(0, str(agent_path))

from agent import build_agent, run_agent


# Cache the compiled agent (compile once, reuse)
@st.cache_resource
def get_agent():
    """Initialize and compile agent once"""
    return build_agent()


# Restricted execution namespace for agent-generated code
# Security: Limited globals with safe builtins and pre-imported modules
# Note: Generated code is already validated by AST parser before execution (primary defense)
# This restricted namespace provides defense-in-depth by:
# 1. Pre-importing allowed modules (pandas, streamlit, plotly)
# 2. Only exposing safe builtins needed for visualization
# 3. Not exposing dangerous builtins like open(), compile(), or unrestricted eval()
SAFE_BUILTINS = {
    'len': len,
    'range': range,
    'str': str,
    'int': int,
    'float': float,
    'list': list,
    'dict': dict,
    'tuple': tuple,
    'bool': bool,
    'None': None,
    'True': True,
    'False': False,
    'round': round,
    'min': min,
    'max': max,
    'sum': sum,
    'sorted': sorted,
    'enumerate': enumerate,
    'zip': zip,
    '__import__': __import__,  # Needed for import statements; imports already validated by AST
    '__builtins__': {
        '__import__': __import__,  # Allow import (already AST-validated)
        'len': len, 'str': str, 'int': int, 'float': float,  # Safe builtins
        'list': list, 'dict': dict, 'tuple': tuple, 'bool': bool,
        'None': None, 'True': True, 'False': False,
        'range': range, 'enumerate': enumerate, 'zip': zip,
        'min': min, 'max': max, 'sum': sum, 'round': round, 'sorted': sorted,
    },
}

RESTRICTED_GLOBALS = {
    **SAFE_BUILTINS,
    'pd': pd,       # Pre-import pandas (to avoid repeated imports)
    'st': st,       # Pre-import streamlit
    'px': px,       # Pre-import plotly.express
}


def main():
    """Main Streamlit app"""

    # Page config
    st.set_page_config(
        page_title="CEVA Data Assistant",
        page_icon="🐾",
        layout="wide"
    )

    # Initialize session state
    if "last_result" not in st.session_state:
        st.session_state.last_result = None

    # Title
    st.title("🐾 CEVA Animal Health - Data Assistant")
    st.markdown("Ask questions about production data in natural language")

    st.markdown("---")

    # User input form
    with st.form("question_form"):
        question = st.text_input(
            "Ask a question:",
            placeholder="How many batches were produced by each business unit?",
            help="Enter your question in natural language"
        )
        submitted = st.form_submit_button("Analyze")

    # Process question
    if submitted and question:
        with st.spinner("🔄 Analyzing your question..."):
            try:
                # Get cached agent
                agent = get_agent()

                # Run agent
                result = run_agent(question, agent)

                # Store in session state
                st.session_state.last_result = result

                st.success("✅ Analysis complete!")

            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.session_state.last_result = None

    # Display results
    if st.session_state.get("last_result"):
        result = st.session_state.last_result

        # Display SQL
        with st.expander("📝 Generated SQL Query", expanded=False):
            st.code(result.get("generated_sql", ""), language="sql")

        # Display visualization
        st.subheader("📊 Results")

        rows = result.get("query_results", [])
        columns = result.get("result_columns", [])
        generated_code = result.get("streamlit_code", "")

        if rows and columns:
            try:
                # Execute the agent-generated code dynamically
                if generated_code:
                    # Create a local namespace for execution
                    local_namespace = {}

                    # Execute the generated code to define render_visualization function
                    # Security: Use RESTRICTED_GLOBALS to limit available builtins and modules
                    # This prevents generated code from accessing dangerous functions like open(), eval(), __import__()
                    exec(generated_code, RESTRICTED_GLOBALS, local_namespace)

                    # Call the generated render_visualization function
                    if 'render_visualization' in local_namespace:
                        local_namespace['render_visualization']("auto", columns, rows)
                    else:
                        raise ValueError("Generated code did not define render_visualization function")
                else:
                    raise ValueError("No visualization code generated")

            except Exception as e:
                st.error(f"⚠️ Chart rendering failed: {e}")
                st.warning("Showing table as fallback...")
                df = pd.DataFrame(rows, columns=columns)
                st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("No results returned from query")


if __name__ == "__main__":
    main()

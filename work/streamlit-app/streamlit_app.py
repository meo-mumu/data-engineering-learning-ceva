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
                    exec(generated_code, {}, local_namespace)

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

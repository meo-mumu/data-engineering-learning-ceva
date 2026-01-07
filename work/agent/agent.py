# Build a Natural Language to SQL agent that queries a DuckDB star schema and generates Streamlit visualizations.
# Use LangGraph for orchestration and HuggingFace Inference API with MODEL_ID = "Qwen/Qwen2.5-Coder-7B-Instruct" for LLM calls.

# 1. manage imports
import os
from pathlib import Path
from typing import TypedDict, Annotated, Literal

import yaml
import duckdb
from dotenv import load_dotenv

from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from nodes import (
    create_generate_sql_node,
    validate_sql,
    create_execute_sql_node,
    create_generate_streamlit_views_node,
)


# State definition
class AgentState(TypedDict):
    """State for the NL to SQL agent"""
    question: str
    generated_sql: str
    sql_valid: bool
    validation_error: str
    retry_count: int
    execution_error: bool
    query_results: list
    result_columns: list
    streamlit_code: str
    messages: Annotated[list, add_messages]


# 2. load env code
load_dotenv()

# Disable LangSmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = "false"

HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_ID = "Qwen/Qwen2.5-Coder-7B-Instruct"
TIMEOUT_SECONDS = 60  # LLM API call timeout (configurable)

if not HF_TOKEN:
    raise ValueError("HF_TOKEN not found in environment variables")

# Paths
WORK_DIR = Path(__file__).parent.parent
AGENT_SPECS_PATH = Path(__file__).parent / "agent-specifications.md"
SEMANTIC_LAYER_PATH = WORK_DIR / "data" / "semantic_layer.yaml"


# Helper functions
def load_agent_specifications() -> str:
    """Load agent specifications as raw text"""
    with open(AGENT_SPECS_PATH, "r") as f:
        return f.read()


def load_semantic_layer() -> str:
    """Load semantic layer YAML and resolve dynamic paths"""
    with open(SEMANTIC_LAYER_PATH, "r") as f:
        content = f.read()

    # Resolve DATA_PATH dynamically (points to work/data directory)
    data_path = WORK_DIR / "data"
    resolved_path = str(data_path.resolve())

    # Replace {DATA_PATH} placeholder with actual path
    content = content.replace("{DATA_PATH}", resolved_path)

    return content


def load_visualization_guidelines() -> str:
    """Load visualization guidelines from agent-specifications.md"""
    with open(AGENT_SPECS_PATH, "r") as f:
        content = f.read()

    # Extract from "## Plotly Visualization Guidelines" to end of file
    start_marker = "## Plotly Visualization Guidelines"
    if start_marker in content:
        viz_section = content.split(start_marker)[1]
        # Include the marker in the returned content
        return start_marker + viz_section
    else:
        return ""  # Fallback if section not found


def initialize_duckdb_connection() -> duckdb.DuckDBPyConnection:
    """Initialize persistent DuckDB connection with views for parquet files"""
    print("📊 Initializing DuckDB connection with views...")

    # Create in-memory connection (reusable)
    conn = duckdb.connect(":memory:")

    # Resolve data path
    data_path = WORK_DIR / "data" / "b-silver-star-schema"
    resolved_path = str(data_path.resolve())

    # Create views for each parquet file
    views = {
        "dim_product": f"{resolved_path}/dim_product.parquet",
        "dim_specie": f"{resolved_path}/dim_specie.parquet",
        "dim_site": f"{resolved_path}/dim_site.parquet",
        "fact_batch_production": f"{resolved_path}/fact_batch_production.parquet",
    }

    for view_name, parquet_path in views.items():
        conn.execute(f"CREATE VIEW {view_name} AS SELECT * FROM read_parquet('{parquet_path}')")
        print(f"  ✓ Created view: {view_name}")

    print("✅ DuckDB views created\n")
    return conn


# 3. Conditional edge functions
def check_sql_validity(state: AgentState) -> Literal["valid", "invalid", "max_retries"]:
    """Route based on SQL validation result and retry count"""
    if state.get("sql_valid", False):
        return "valid"

    # Check if max retries exceeded
    retry_count = state.get("retry_count", 0)
    if retry_count >= 3:
        return "max_retries"

    return "invalid"


def max_retries_exceeded(state: AgentState) -> AgentState:
    """Handle max retries exceeded - return error message"""
    error_msg = (
        f"Failed to generate valid SQL after {state.get('retry_count', 0)} attempts. "
        f"Last error: {state.get('validation_error', 'Unknown error')}"
    )
    print(f"\n❌ {error_msg}\n")

    # Set error in state for Streamlit to display
    state["validation_error"] = error_msg
    state["generated_sql"] = ""

    return state


def check_execution_success(state: AgentState) -> Literal["success", "error"]:
    """Route based on SQL execution result"""
    return "error" if state.get("execution_error", False) else "success"


def handle_execution_error(state: AgentState) -> AgentState:
    """Handle SQL execution error - format user-friendly message"""
    error_msg = state.get("validation_error", "Unknown SQL execution error")
    print(f"\n❌ Execution error: {error_msg}\n")

    # Error already stored in validation_error by execute_sql node
    # Just ensure empty results
    state["query_results"] = []
    state["result_columns"] = []

    return state


# 4. Build and run functions
def build_agent():
    """Build and compile the LangGraph agent (called once)"""
    # Load specifications and semantic layer
    print("📖 Loading agent specifications and semantic layer...")
    agent_specs = load_agent_specifications()
    semantic_layer = load_semantic_layer()
    viz_guidelines = load_visualization_guidelines()
    print("✅ Loaded successfully\n")

    # Initialize DuckDB connection with views
    conn = initialize_duckdb_connection()

    # Initialize the LLM endpoint
    llm_endpoint = HuggingFaceEndpoint(
        repo_id=MODEL_ID,
        huggingfacehub_api_token=HF_TOKEN,
        temperature=0.1,
        max_new_tokens=2048,
        timeout=TIMEOUT_SECONDS,
    )

    # Wrap with ChatHuggingFace for conversational interface
    llm = ChatHuggingFace(llm=llm_endpoint)

    # Build the StateGraph
    workflow = StateGraph(AgentState)

    # Create nodes with dependencies
    generate_sql_node = create_generate_sql_node(llm, agent_specs, semantic_layer)
    execute_sql_node = create_execute_sql_node(conn)
    generate_viz_node = create_generate_streamlit_views_node(llm, viz_guidelines)

    # Add nodes
    workflow.add_node("generate_sql", generate_sql_node)
    workflow.add_node("validate_sql", validate_sql)
    workflow.add_node("execute_sql", execute_sql_node)
    workflow.add_node("generate_streamlit_views", generate_viz_node)
    workflow.add_node("max_retries_exceeded", max_retries_exceeded)
    workflow.add_node("handle_execution_error", handle_execution_error)

    # Define the flow with conditional edges
    workflow.add_edge(START, "generate_sql")
    workflow.add_edge("generate_sql", "validate_sql")

    # Conditional edge: if valid -> execute, if invalid -> retry or fail
    workflow.add_conditional_edges(
        "validate_sql",
        check_sql_validity,
        {
            "valid": "execute_sql",
            "invalid": "generate_sql",  # Retry loop (if retry_count < 3)
            "max_retries": "max_retries_exceeded",  # Exit on max retries
        }
    )

    # Conditional edge: if execution succeeds -> generate viz, if fails -> handle error
    workflow.add_conditional_edges(
        "execute_sql",
        check_execution_success,
        {
            "success": "generate_streamlit_views",
            "error": "handle_execution_error",
        }
    )

    workflow.add_edge("generate_streamlit_views", END)
    workflow.add_edge("max_retries_exceeded", END)
    workflow.add_edge("handle_execution_error", END)

    # Compile and return the graph
    return workflow.compile()


def run_agent(question: str, compiled_app=None):
    """Run the agent with a question and return results

    Args:
        question: Natural language question
        compiled_app: Pre-compiled LangGraph app (optional, will build if None)

    Returns:
        AgentState dict with query_results, result_columns, generated_sql, streamlit_code
    """
    if compiled_app is None:
        compiled_app = build_agent()

    initial_state = {
        "question": question,
        "generated_sql": "",
        "sql_valid": False,
        "validation_error": "",
        "retry_count": 0,
        "execution_error": False,
        "query_results": [],
        "result_columns": [],
        "streamlit_code": "",
        "messages": [],
    }

    return compiled_app.invoke(initial_state)


def main():
    """CLI entry point for testing"""
    # Build agent once
    app = build_agent()

    # Test with a simple question
    question = "How many batches were produced by each business unit?"
    print(f"\n🚀 Running agent with question: {question}\n")

    # Run the agent
    result = run_agent(question, app)

    print(f"\n✅ Agent completed!")
    print(f"\nGenerated SQL:\n{result.get('generated_sql', 'N/A')}")
    print(f"\nQuery Results:")
    print(f"Columns: {result.get('result_columns', [])}")
    print(f"Rows: {result.get('query_results', [])}")
    print(f"\nStreamlit code generated: {len(result.get('streamlit_code', ''))} characters")


if __name__ == "__main__":
    main()
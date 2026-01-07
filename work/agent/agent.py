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
    execute_sql,
    generate_streamlit_views,
)


# State definition
class AgentState(TypedDict):
    """State for the NL to SQL agent"""
    question: str
    generated_sql: str
    sql_valid: bool
    validation_error: str
    query_results: list
    result_columns: list
    viz_type: str
    streamlit_code: str
    messages: Annotated[list, add_messages]


# 2. load env code
load_dotenv()

# Disable LangSmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = "false"

HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_ID = "Qwen/Qwen2.5-Coder-7B-Instruct"

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
    """Load semantic layer YAML as raw text"""
    with open(SEMANTIC_LAYER_PATH, "r") as f:
        return f.read()


# 3. Conditional edge functions
def check_sql_validity(state: AgentState) -> Literal["valid", "invalid"]:
    """Route based on SQL validation result"""
    return "valid" if state.get("sql_valid", False) else "invalid"


# 4. Build and run functions
def build_agent():
    """Build and compile the LangGraph agent (called once)"""
    # Load specifications and semantic layer
    print("📖 Loading agent specifications and semantic layer...")
    agent_specs = load_agent_specifications()
    semantic_layer = load_semantic_layer()
    print("✅ Loaded successfully\n")

    # Initialize the LLM endpoint
    llm_endpoint = HuggingFaceEndpoint(
        repo_id=MODEL_ID,
        huggingfacehub_api_token=HF_TOKEN,
        temperature=0.1,
        max_new_tokens=2048,
    )

    # Wrap with ChatHuggingFace for conversational interface
    llm = ChatHuggingFace(llm=llm_endpoint)

    # Build the StateGraph
    workflow = StateGraph(AgentState)

    # Create nodes with dependencies
    generate_sql_node = create_generate_sql_node(llm, agent_specs, semantic_layer)

    # Add nodes
    workflow.add_node("generate_sql", generate_sql_node)
    workflow.add_node("validate_sql", validate_sql)
    workflow.add_node("execute_sql", execute_sql)
    workflow.add_node("generate_streamlit_views", generate_streamlit_views)

    # Define the flow with conditional edges
    workflow.add_edge(START, "generate_sql")
    workflow.add_edge("generate_sql", "validate_sql")

    # Conditional edge: if valid -> execute, if invalid -> regenerate
    workflow.add_conditional_edges(
        "validate_sql",
        check_sql_validity,
        {
            "valid": "execute_sql",
            "invalid": "generate_sql",  # Retry loop
        }
    )

    workflow.add_edge("execute_sql", "generate_streamlit_views")
    workflow.add_edge("generate_streamlit_views", END)

    # Compile and return the graph
    return workflow.compile()


def run_agent(question: str, compiled_app=None):
    """Run the agent with a question and return results

    Args:
        question: Natural language question
        compiled_app: Pre-compiled LangGraph app (optional, will build if None)

    Returns:
        AgentState dict with query_results, result_columns, generated_sql, viz_type
    """
    if compiled_app is None:
        compiled_app = build_agent()

    initial_state = {
        "question": question,
        "generated_sql": "",
        "sql_valid": False,
        "validation_error": "",
        "query_results": [],
        "result_columns": [],
        "viz_type": "",
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
    print(f"\nVisualization type: {result.get('viz_type', 'N/A')}")


if __name__ == "__main__":
    main()
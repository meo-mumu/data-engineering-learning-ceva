"""Test timeout handling for LLM API calls"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from nodes.generate_sql import create_generate_sql_node
from nodes.generate_streamlit_views import create_generate_streamlit_views_node, generate_safe_table_fallback


def test_generate_sql_timeout_handling():
    """Test that generate_sql handles timeout gracefully"""
    print("Testing generate_sql timeout handling...")

    # Create mock LLM that raises TimeoutError
    mock_llm = Mock()
    mock_llm.invoke.side_effect = TimeoutError("Request timed out after 60 seconds")

    # Create the node
    generate_sql = create_generate_sql_node(
        mock_llm,
        agent_specs="Test specs",
        semantic_layer="Test schema"
    )

    # Create initial state
    state = {
        "question": "Test question",
        "generated_sql": "",
        "sql_valid": False,
        "validation_error": "",
        "retry_count": 0,
    }

    # Call the node
    result = generate_sql(state)

    # Verify timeout was handled
    assert result["validation_error"] == "LLM timeout, please retry", \
        f"Expected timeout error message, got: {result['validation_error']}"
    assert result["generated_sql"] == "", "SQL should be empty on timeout"
    assert result["sql_valid"] is False, "sql_valid should be False on timeout"

    print("✅ generate_sql handles TimeoutError correctly")


def test_generate_sql_network_error_handling():
    """Test that generate_sql handles network errors"""
    print("Testing generate_sql network error handling...")

    # Create mock LLM that raises a generic exception with "timeout" in message
    mock_llm = Mock()
    mock_llm.invoke.side_effect = Exception("Connection timed out")

    # Create the node
    generate_sql = create_generate_sql_node(
        mock_llm,
        agent_specs="Test specs",
        semantic_layer="Test schema"
    )

    # Create initial state
    state = {
        "question": "Test question",
        "generated_sql": "",
        "sql_valid": False,
        "validation_error": "",
        "retry_count": 0,
    }

    # Call the node
    result = generate_sql(state)

    # Verify timeout was detected in error message
    assert result["validation_error"] == "LLM timeout, please retry", \
        f"Expected timeout error message, got: {result['validation_error']}"
    assert result["generated_sql"] == "", "SQL should be empty on timeout"

    print("✅ generate_sql detects timeout in error messages")


def test_generate_streamlit_views_timeout_handling():
    """Test that generate_streamlit_views handles timeout gracefully"""
    print("Testing generate_streamlit_views timeout handling...")

    # Create mock LLM that raises TimeoutError
    mock_llm = Mock()
    mock_llm.invoke.side_effect = TimeoutError("Request timed out after 60 seconds")

    # Create the node
    generate_viz = create_generate_streamlit_views_node(
        mock_llm,
        viz_guidelines="Test guidelines"
    )

    # Create initial state with sample data
    state = {
        "question": "Test question",
        "generated_sql": "SELECT * FROM test",
        "query_results": [("row1", 1), ("row2", 2)],
        "result_columns": ["name", "value"],
        "streamlit_code": "",
    }

    # Call the node
    result = generate_viz(state)

    # Verify timeout was handled with fallback
    assert "streamlit_code" in result, "streamlit_code should be in result"
    assert len(result["streamlit_code"]) > 0, "Should have fallback code"
    assert "def render_visualization" in result["streamlit_code"], \
        "Fallback should define render_visualization function"

    # Verify it's the safe table fallback
    expected_fallback = generate_safe_table_fallback(["name", "value"])
    assert result["streamlit_code"] == expected_fallback, \
        "Should use safe table fallback on timeout"

    print("✅ generate_streamlit_views handles TimeoutError with safe fallback")


def test_timeout_constant_configured():
    """Test that TIMEOUT_SECONDS constant is configured in agent.py"""
    print("Testing TIMEOUT_SECONDS configuration...")

    # Import agent module
    import agent

    # Verify constant exists
    assert hasattr(agent, 'TIMEOUT_SECONDS'), "TIMEOUT_SECONDS should be defined in agent.py"
    assert isinstance(agent.TIMEOUT_SECONDS, int), "TIMEOUT_SECONDS should be an integer"
    assert agent.TIMEOUT_SECONDS > 0, "TIMEOUT_SECONDS should be positive"
    assert agent.TIMEOUT_SECONDS == 60, "TIMEOUT_SECONDS should be 60 by default"

    print(f"✅ TIMEOUT_SECONDS configured: {agent.TIMEOUT_SECONDS} seconds")


def main():
    print("=" * 60)
    print("Timeout Handling Test Suite")
    print("=" * 60 + "\n")

    test_timeout_constant_configured()
    test_generate_sql_timeout_handling()
    test_generate_sql_network_error_handling()
    test_generate_streamlit_views_timeout_handling()

    print("\n" + "=" * 60)
    print("✅ ALL TIMEOUT TESTS PASSED")
    print("LLM API calls are properly protected against timeouts!")
    print("=" * 60)


if __name__ == "__main__":
    main()

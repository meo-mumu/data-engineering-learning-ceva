"""Comprehensive verification that timeout handling is properly implemented"""

import sys
from pathlib import Path
import inspect

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent / "agent"))


def test_timeout_constant_exists():
    """Verify TIMEOUT_SECONDS constant is defined"""
    print("Checking TIMEOUT_SECONDS constant...")

    import agent

    assert hasattr(agent, 'TIMEOUT_SECONDS'), "TIMEOUT_SECONDS not found in agent.py"
    assert agent.TIMEOUT_SECONDS == 60, f"Expected TIMEOUT_SECONDS=60, got {agent.TIMEOUT_SECONDS}"

    print(f"✅ TIMEOUT_SECONDS = {agent.TIMEOUT_SECONDS} seconds")


def test_huggingface_endpoint_configured():
    """Verify HuggingFaceEndpoint is configured with timeout"""
    print("\nChecking HuggingFaceEndpoint configuration...")

    # Read agent.py source
    agent_file = Path(__file__).parent / "agent.py"
    with open(agent_file, "r") as f:
        content = f.read()

    # Check that timeout is passed to HuggingFaceEndpoint
    assert "timeout=TIMEOUT_SECONDS" in content, \
        "HuggingFaceEndpoint not configured with timeout parameter"

    print("✅ HuggingFaceEndpoint configured with timeout=TIMEOUT_SECONDS")


def test_generate_sql_has_timeout_handling():
    """Verify generate_sql.py has timeout exception handling"""
    print("\nChecking generate_sql timeout handling...")

    # Read generate_sql.py source
    sql_file = Path(__file__).parent / "nodes" / "generate_sql.py"
    with open(sql_file, "r") as f:
        content = f.read()

    # Check for TimeoutError handling
    assert "except TimeoutError" in content, \
        "TimeoutError exception handler not found in generate_sql.py"

    # Check for timeout error message
    assert "LLM timeout, please retry" in content, \
        "Timeout error message not found in generate_sql.py"

    # Check for timeout detection in general exceptions
    assert '"timeout"' in content.lower() or "'timeout'" in content.lower(), \
        "Timeout detection in error messages not found in generate_sql.py"

    print("✅ generate_sql has proper timeout handling")
    print("  - TimeoutError exception handler ✓")
    print("  - Timeout error message ✓")
    print("  - Timeout detection in error strings ✓")


def test_generate_streamlit_views_has_timeout_handling():
    """Verify generate_streamlit_views.py has timeout exception handling"""
    print("\nChecking generate_streamlit_views timeout handling...")

    # Read generate_streamlit_views.py source
    viz_file = Path(__file__).parent / "nodes" / "generate_streamlit_views.py"
    with open(viz_file, "r") as f:
        content = f.read()

    # Check for TimeoutError handling
    assert "except TimeoutError" in content, \
        "TimeoutError exception handler not found in generate_streamlit_views.py"

    # Check for safe fallback on timeout
    assert "generate_safe_table_fallback" in content, \
        "Safe table fallback not found in generate_streamlit_views.py"

    # Check for timeout detection in general exceptions
    assert '"timeout"' in content.lower() or "'timeout'" in content.lower(), \
        "Timeout detection in error messages not found in generate_streamlit_views.py"

    print("✅ generate_streamlit_views has proper timeout handling")
    print("  - TimeoutError exception handler ✓")
    print("  - Safe table fallback ✓")
    print("  - Timeout detection in error strings ✓")


def test_timeout_behavior_generate_sql():
    """Verify generate_sql timeout behavior with mock"""
    print("\nTesting generate_sql timeout behavior...")

    from unittest.mock import Mock
    from nodes.generate_sql import create_generate_sql_node

    # Create mock LLM that times out
    mock_llm = Mock()
    mock_llm.invoke.side_effect = TimeoutError("Test timeout")

    # Create node
    generate_sql = create_generate_sql_node(mock_llm, "specs", "schema")

    # Test state
    state = {
        "question": "Test",
        "generated_sql": "",
        "sql_valid": False,
        "validation_error": "",
        "retry_count": 0,
    }

    # Execute
    result = generate_sql(state)

    # Verify behavior
    assert result["validation_error"] == "LLM timeout, please retry", \
        f"Wrong error message: {result['validation_error']}"
    assert result["generated_sql"] == "", \
        f"SQL should be empty, got: {result['generated_sql']}"
    assert result["sql_valid"] is False, \
        "sql_valid should be False on timeout"

    print("✅ generate_sql timeout behavior correct")
    print(f"  - Error message: '{result['validation_error']}'")
    print(f"  - SQL cleared: {result['generated_sql'] == ''}")
    print(f"  - sql_valid=False: {result['sql_valid'] is False}")


def test_timeout_behavior_generate_viz():
    """Verify generate_streamlit_views timeout behavior with mock"""
    print("\nTesting generate_streamlit_views timeout behavior...")

    from unittest.mock import Mock
    from nodes.generate_streamlit_views import create_generate_streamlit_views_node

    # Create mock LLM that times out
    mock_llm = Mock()
    mock_llm.invoke.side_effect = TimeoutError("Test timeout")

    # Create node
    generate_viz = create_generate_streamlit_views_node(mock_llm, "guidelines")

    # Test state
    state = {
        "question": "Test",
        "generated_sql": "SELECT 1",
        "query_results": [("test", 1)],
        "result_columns": ["name", "value"],
        "streamlit_code": "",
    }

    # Execute
    result = generate_viz(state)

    # Verify behavior
    assert "streamlit_code" in result, "streamlit_code missing from result"
    assert len(result["streamlit_code"]) > 0, "streamlit_code should not be empty"
    assert "def render_visualization" in result["streamlit_code"], \
        "Fallback code should define render_visualization"
    assert "st.dataframe" in result["streamlit_code"], \
        "Fallback should use st.dataframe for table"

    print("✅ generate_streamlit_views timeout behavior correct")
    print(f"  - Code generated: {len(result['streamlit_code'])} chars")
    print(f"  - Has render_visualization: {'render_visualization' in result['streamlit_code']}")
    print(f"  - Uses safe fallback: {'st.dataframe' in result['streamlit_code']}")


def main():
    print("=" * 70)
    print("Comprehensive Timeout Handling Verification")
    print("=" * 70)

    try:
        test_timeout_constant_exists()
        test_huggingface_endpoint_configured()
        test_generate_sql_has_timeout_handling()
        test_generate_streamlit_views_has_timeout_handling()
        test_timeout_behavior_generate_sql()
        test_timeout_behavior_generate_viz()

        print("\n" + "=" * 70)
        print("✅ ALL VERIFICATION CHECKS PASSED")
        print("=" * 70)
        print("\nTimeout handling is fully implemented:")
        print("  ✓ TIMEOUT_SECONDS constant configured (60s)")
        print("  ✓ HuggingFaceEndpoint uses timeout parameter")
        print("  ✓ generate_sql catches timeouts and sets error message")
        print("  ✓ generate_streamlit_views catches timeouts and uses fallback")
        print("  ✓ Both nodes detect timeout in error strings")
        print("  ✓ App will not hang on slow/down API")
        print("=" * 70)

    except AssertionError as e:
        print(f"\n❌ VERIFICATION FAILED: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

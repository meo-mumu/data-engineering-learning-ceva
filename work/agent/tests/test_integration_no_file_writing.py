"""Integration test - verify agent doesn't write to streamlit file"""

import sys
from pathlib import Path

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent import build_agent, run_agent


def test_agent_stores_code_in_state():
    """Test that agent generates code and stores it in state only"""

    print("Building agent...")
    app = build_agent()

    print("Running agent with test question...")
    question = "How many batches were produced by each business unit?"
    result = run_agent(question, app)

    # Verify code is in state
    assert "streamlit_code" in result, "streamlit_code should be in result state"
    code = result["streamlit_code"]
    assert len(code) > 0, "Generated code should not be empty"
    assert "def render_visualization" in code, "Code should define render_visualization function"

    print(f"✅ Code stored in state: {len(code)} characters")
    print(f"✅ Function signature present: {'render_visualization' in code}")

    return result


def test_code_is_executable():
    """Test that the generated code can be executed dynamically"""

    print("\nTesting code execution...")

    # Use result from previous test
    app = build_agent()
    question = "How many batches were produced by each business unit?"
    result = run_agent(question, app)

    code = result["streamlit_code"]
    rows = result["query_results"]
    columns = result["result_columns"]

    # Execute the code (simulating streamlit execution)
    local_namespace = {}
    exec(code, {}, local_namespace)

    assert "render_visualization" in local_namespace, "Code should define render_visualization"

    # Note: We can't actually call it here because streamlit isn't available
    # But we've verified it's defined correctly
    print("✅ Generated code is executable")
    print(f"✅ Function defined in namespace: {list(local_namespace.keys())}")


def test_no_file_writing():
    """Verify that streamlit_app.py is NOT modified during agent execution"""

    streamlit_file = Path(__file__).parent.parent / "streamlit-app" / "streamlit_app.py"

    # Read file before
    with open(streamlit_file, "r") as f:
        content_before = f.read()

    # Get modification time before
    mtime_before = streamlit_file.stat().st_mtime

    print(f"\nStreamlit file before: {len(content_before)} bytes, modified at {mtime_before}")

    # Run agent
    app = build_agent()
    question = "Show me batch status distribution"
    result = run_agent(question, app)

    # Read file after
    with open(streamlit_file, "r") as f:
        content_after = f.read()

    # Get modification time after
    mtime_after = streamlit_file.stat().st_mtime

    print(f"Streamlit file after:  {len(content_after)} bytes, modified at {mtime_after}")

    # Verify no changes
    assert content_before == content_after, "Streamlit file should NOT be modified"
    assert mtime_before == mtime_after, "File modification time should NOT change"

    print("✅ Streamlit file NOT modified - decoupling successful!")


def main():
    print("=" * 60)
    print("Integration Test - No File Writing")
    print("=" * 60 + "\n")

    test_agent_stores_code_in_state()
    test_code_is_executable()
    test_no_file_writing()

    print("\n" + "=" * 60)
    print("✅ ALL INTEGRATION TESTS PASSED")
    print("Agent successfully decoupled from file writing!")
    print("=" * 60)


if __name__ == "__main__":
    main()

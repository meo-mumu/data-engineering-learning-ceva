"""Test security validation for generated code"""

import sys
from pathlib import Path

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent / "agent"))

from nodes.generate_streamlit_views import validate_generated_code


def test_direct_function_calls():
    """Test detection of direct forbidden function calls (ast.Name)"""
    print("Testing direct function calls (ast.Name)...")

    # Should be blocked
    blocked_cases = [
        ("eval('code')", "eval"),
        ("exec('code')", "exec"),
        ("__import__('os')", "__import__"),
        ("open('/etc/passwd')", "open"),
        ("compile('code', 'file', 'exec')", "compile"),
    ]

    for code, expected_func in blocked_cases:
        full_code = f"""
def render_visualization(viz_type: str, columns: list, rows: list):
    {code}
"""
        is_valid, error = validate_generated_code(full_code)
        assert not is_valid, f"FAILED: {code} should be blocked"
        assert expected_func in error.lower(), f"FAILED: Error message should mention {expected_func}"
        print(f"  ✓ Blocked: {code}")

    print("✅ All direct function call tests passed\n")


def test_method_calls():
    """Test detection of module.method calls (ast.Attribute)"""
    print("Testing method calls (ast.Attribute)...")

    # Should be blocked
    blocked_cases = [
        ("os.system('rm -rf /')", "os.system"),
        ("os.popen('cat /etc/passwd')", "os.popen"),
        ("os.execv('/bin/sh', [])", "os.execv"),
        ("os.spawnl(0, '/bin/sh')", "os.spawnl"),
        ("subprocess.run(['rm', '-rf', '/'])", "subprocess.run"),
        ("subprocess.Popen(['malicious'])", "subprocess.Popen"),
        ("subprocess.call(['cmd'])", "subprocess.call"),
        ("builtins.__import__('os')", "builtins.__import__"),
    ]

    for code, expected_call in blocked_cases:
        full_code = f"""
def render_visualization(viz_type: str, columns: list, rows: list):
    {code}
"""
        is_valid, error = validate_generated_code(full_code)
        assert not is_valid, f"FAILED: {code} should be blocked"
        print(f"  ✓ Blocked: {code} → {error}")

    print("✅ All method call tests passed\n")


def test_allowed_calls():
    """Test that allowed calls pass validation"""
    print("Testing allowed calls...")

    allowed_code = """
def render_visualization(viz_type: str, columns: list, rows: list):
    import pandas as pd
    import streamlit as st
    import plotly.express as px

    df = pd.DataFrame(rows, columns=columns)
    fig = px.bar(df, x=columns[0], y=columns[1])
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Total: {len(df)} rows")
"""

    is_valid, error = validate_generated_code(allowed_code)
    assert is_valid, f"FAILED: Valid code should pass validation. Error: {error}"
    print("  ✓ Allowed: Valid pandas/streamlit/plotly code")

    print("✅ All allowed call tests passed\n")


def main():
    print("=" * 60)
    print("Security Validation Test Suite")
    print("=" * 60 + "\n")

    test_direct_function_calls()
    test_method_calls()
    test_allowed_calls()

    print("=" * 60)
    print("✅ ALL TESTS PASSED - Security validation working correctly")
    print("=" * 60)


if __name__ == "__main__":
    main()

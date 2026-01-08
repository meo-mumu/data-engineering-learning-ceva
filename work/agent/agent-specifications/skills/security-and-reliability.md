# Security & Reliability

## 3-Layer Security Defense

The agent implements defense-in-depth for LLM-generated visualization code execution:

### Layer 1: LLM Generation (First Line)
- LLM prompted to generate safe code using only pandas, streamlit, plotly.express
- Instructed to avoid file I/O, network calls, system operations
- Not relied upon for security (LLMs can make mistakes)

### Layer 2: AST Validation (Primary Defense)
- Parses and validates generated code BEFORE execution using Python AST parser
- Enforces import whitelist: Only allows pandas, streamlit, plotly.express
- Blocks forbidden imports: `os`, `sys`, `subprocess`, `builtins.__import__`
- Blocks forbidden function calls: `eval()`, `exec()`, `compile()`, `open()`
- Blocks forbidden method calls: `os.system()`, `subprocess.run()`, `builtins.eval()`
- Validates function signature: Ensures `render_visualization(viz_type, columns, rows)` exists
- **Code never reaches execution if validation fails**

### Layer 3: Restricted Namespace (Defense-in-Depth)
- Executes generated code with restricted `globals()` dictionary
- Only exposes safe builtins: `len`, `str`, `int`, `float`, `list`, `dict`, `min`, `max`, `sum`, `range`, `enumerate`, `zip`, `sorted`
- Pre-imports allowed modules: `pd`, `st`, `px` (to avoid repeated imports)
- Blocks dangerous builtins: `open`, `eval`, `exec`, `compile`
- `__import__` allowed because imports are already validated by AST (Layer 2)

### Security Guarantees
- ✅ No file system access from generated code
- ✅ No network access from generated code
- ✅ No system command execution
- ✅ No arbitrary code evaluation (`eval`, `exec`)
- ✅ No dangerous module imports (`os`, `subprocess`, `sys`)

### Test Coverage
- `tests/test_security_validation.py`: 21 AST validation test cases
- `tests/test_malicious_code_detection.py`: 5 malicious payload scenarios
- `tests/test_restricted_exec.py`: 6 namespace restriction tests

## Timeout Handling

### Configuration
- **60 seconds** timeout on all LLM API calls (configurable via `TIMEOUT_SECONDS` in `agent.py`)
- Prevents application from hanging on slow/down API

### Behavior on Timeout

**SQL Generation Timeout:**
- Catches `TimeoutError` and timeout-related exceptions
- Sets `validation_error = "LLM timeout, please retry"`
- Sets `generated_sql = ""`
- Sets `sql_valid = False`
- User sees clear error message and can retry immediately

**Visualization Generation Timeout:**
- Catches `TimeoutError` and timeout-related exceptions
- Falls back to safe table view using `generate_safe_table_fallback()`
- Logs timeout with ⏱️ emoji for debugging
- User still sees their data (in table format instead of chart)

### Test Coverage
- `tests/test_timeout_handling.py`: Verifies timeout behavior for both SQL and visualization generation

## Performance Optimizations

### DuckDB Persistent Connection
- Single connection initialized at agent startup
- Pre-creates views for all parquet files (`dim_product`, `dim_specie`, `dim_site`, `fact_batch_production`)
- Eliminates repeated parquet scanning on each query
- Uses `read_parquet()` only once per table

### Dynamic Code Execution
- Generated visualization code executed via `exec()` with restricted namespace
- No file writing to disk
- Supports concurrent users (each session has isolated namespace)

### Cached Agent
- LangGraph agent compiled once and cached via `@st.cache_resource`
- Reused across all user requests
- Reduces startup latency

# Timeout Handling for LLM API Calls

## Overview

This document describes the timeout handling implementation for LLM API calls in the CEVA Data Assistant agent.

## Problem

LLM calls to the HuggingFace Inference API had no timeout protection. If the API was slow or down, the application would hang indefinitely, causing poor user experience.

## Solution

Implemented comprehensive timeout handling across all LLM API calls with graceful fallback mechanisms.

## Changes Made

### 1. Configuration (`work/agent/agent.py`)

**Added timeout constant:**
```python
TIMEOUT_SECONDS = 60  # LLM API call timeout (configurable)
```

**Configured HuggingFaceEndpoint with timeout:**
```python
llm_endpoint = HuggingFaceEndpoint(
    repo_id=MODEL_ID,
    huggingfacehub_api_token=HF_TOKEN,
    temperature=0.1,
    max_new_tokens=2048,
    timeout=TIMEOUT_SECONDS,  # NEW
)
```

### 2. SQL Generation Timeout Handling (`work/agent/nodes/generate_sql.py`)

**Wrapped llm.invoke() with try/except:**
```python
try:
    response = llm.invoke(prompt)
    generated_text = response.content.strip()
except TimeoutError as e:
    print(f"⏱️  LLM timeout: {e}")
    state["validation_error"] = "LLM timeout, please retry"
    state["generated_sql"] = ""
    state["sql_valid"] = False
    return state
except Exception as e:
    error_msg = str(e)
    if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
        print(f"⏱️  LLM timeout (caught as general exception): {e}")
        state["validation_error"] = "LLM timeout, please retry"
    else:
        print(f"❌ LLM invocation failed: {e}")
        state["validation_error"] = f"LLM error: {error_msg}"
    state["generated_sql"] = ""
    state["sql_valid"] = False
    return state
```

**Behavior on timeout:**
- Sets `validation_error = "LLM timeout, please retry"`
- Sets `generated_sql = ""`
- Sets `sql_valid = False`
- Returns early to prevent further processing
- User sees clear error message

### 3. Visualization Generation Timeout Handling (`work/agent/nodes/generate_streamlit_views.py`)

**Enhanced existing try/except with timeout detection:**
```python
try:
    response = llm.invoke(prompt)
    generated_code = extract_python_code(response.content)
except TimeoutError as e:
    print(f"⏱️  LLM timeout: {e}. Using safe table fallback.")
    generated_code = generate_safe_table_fallback(columns)
    state["streamlit_code"] = generated_code
    return state
except Exception as e:
    error_msg = str(e)
    if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
        print(f"⏱️  LLM timeout (caught as general exception): {e}. Using safe table fallback.")
    else:
        print(f"❌ LLM invocation failed: {e}. Using safe table fallback.")
    generated_code = generate_safe_table_fallback(columns)
    state["streamlit_code"] = generated_code
    return state
```

**Behavior on timeout:**
- Logs timeout with ⏱️ emoji
- Uses `generate_safe_table_fallback()` for guaranteed visualization
- Sets `streamlit_code` with safe fallback
- Returns early with working code
- User sees table view instead of chart

## Timeout Detection Strategy

The implementation catches timeouts in two ways:

1. **Direct TimeoutError:** Catches native Python `TimeoutError` exceptions
2. **String matching:** Detects "timeout" or "timed out" in error messages for wrapped exceptions

This dual approach ensures we catch timeouts regardless of how they're raised by the underlying libraries (requests, httpx, etc.).

## Configuration

To change the timeout duration, modify the constant in `agent.py`:

```python
TIMEOUT_SECONDS = 60  # Increase for slower connections, decrease for faster failure
```

**Recommended values:**
- Development: 30-60 seconds
- Production (fast network): 60 seconds
- Production (slow network): 90-120 seconds

## Testing

Run the timeout handling test suite:

```bash
python work/agent/test_timeout_handling.py
```

**Test coverage:**
- ✅ TIMEOUT_SECONDS constant is configured
- ✅ generate_sql handles TimeoutError correctly
- ✅ generate_sql detects timeout in error messages
- ✅ generate_streamlit_views handles TimeoutError with safe fallback

## User Experience

### Before (No Timeout Handling)
```
User: "Show me batches by business unit"
[API is slow/down]
[App hangs indefinitely]
[User frustrated, closes browser]
```

### After (With Timeout Handling)
```
User: "Show me batches by business unit"
[API timeout after 60s]
⏱️  LLM timeout: Request timed out after 60 seconds
❌ Error: LLM timeout, please retry
[User can retry immediately or try different question]
```

## Error Messages

### For SQL Generation
- Timeout: `"LLM timeout, please retry"`
- Other errors: `"LLM error: {error_message}"`

### For Visualization Generation
- Any error (including timeout): Falls back to safe table view silently
- Logs timeout with ⏱️ emoji for debugging

## Architecture

```
User Question
     ↓
generate_sql (with timeout)
     ↓
   [If timeout → Error message, user can retry]
     ↓
   [If success → Continue]
     ↓
execute_sql
     ↓
generate_streamlit_views (with timeout)
     ↓
   [If timeout → Safe table fallback]
     ↓
   [If success → Generated visualization]
     ↓
Display to user
```

## Benefits

1. **No Hanging:** App never hangs indefinitely on slow API
2. **Clear Feedback:** Users see timeout messages instead of loading spinner
3. **Graceful Degradation:** Visualization falls back to table view
4. **Retryable:** Users can retry immediately
5. **Configurable:** Timeout duration can be adjusted per environment
6. **Resilient:** Multiple detection strategies catch all timeout scenarios

## Monitoring

Timeout events are logged with the ⏱️ emoji for easy identification:

```bash
grep "⏱️" agent.log  # Find all timeout events
```

## Future Improvements

1. **Retry Logic:** Automatic retry with exponential backoff
2. **Circuit Breaker:** Temporarily disable LLM calls if many timeouts occur
3. **Fallback Models:** Try different model if primary times out
4. **Timeout Metrics:** Track timeout frequency for monitoring
5. **User Notification:** Show timeout stats in Streamlit UI

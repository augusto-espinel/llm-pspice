# Response Duplication Bug Fix

## Issue

User reported: "I still get duplicated responses every time I write a prompt on the app"

## Root Cause

**Location:** `app.py` lines 204-226

The app was displaying code blocks twice:

1. **Line 204:** `st.write(response)` - Writes the FULL LLM response with markdown-formatted code block
2. **Line 226:** `st.code(circuit_code, language='python')` - Writes the code block again as syntax-highlighted code

This resulted in:
```
Here's a simple RC circuit:

```python
# First display via st.write
from PySpice.Spice.Netlist import Circuit
...

# Second display via st.code  <-- DUPLICATE!
from PySpice.Spice.Netlist import Circuit
...
```
```

## Fix Applied

**New Logic (app.py lines 205-255):**

```python
# Parse response to avoid code duplication
if '```python' in response and '```' in response:
    # Extract code blocks and non-code text
    code_blocks = []
    parts = response.split('```')
    non_code_parts = []

    for i, part in enumerate(parts):
        if part.startswith('python'):
            # This is a python code block
            code = part[6:].strip()
            code_blocks.append(code)
        elif part.strip():
            # Non-code text
            non_code_parts.append(part)

    # Write only the non-code text (no markdown code block)
    if non_code_parts:
        st.write('\n'.join(non_code_parts))

    # Store code for simulation (use first code block only)
    if code_blocks:
        circuit_code = code_blocks[0]
        st.session_state.circuit_code = circuit_code

        # Show generated code (only once, not duplicated)
        st.code(circuit_code, language='python')
else:
    # No code block - just write the response as-is
    st.write(response)
```

**Result:**
- Non-code text: Displayed once via `st.write()`
- Code block: Displayed once via `st.code()` (syntax-highlighted)
- **No duplication**

## Issues Logging

Added new issue type: `response_duplication`

**In `app_logger.py`:**
```python
def log_response_duplication(prompt, llm_response="", llm_model="", provider="", details=""):
    """Log response duplication issue"""
    logger.log_issue(
        prompt=prompt,
        issue_type="response_duplication",
        error_message=details if details else "LLM response appears to be duplicated",
        llm_response=llm_response,
        llm_model=llm_model,
        provider=provider
    )
```

**Usage in app.py:**
```python
from app_logger import log_response_duplication, ...
```

Note: This fix PREVENTS the issue from occurring, so logger is not actively called. The logger is available for detecting other types of duplication (e.g., if LLM itself generates duplicate code blocks in its response).

## Testing

**To test:**
1. Open app: `streamlit run app.py`
2. Enter any circuit request (e.g., "Create a simple RC circuit")
3. Verify:
   - Text explanation appears once
   - Code block appears once (syntax-highlighted)
   - No duplication

**Expected output:**
```
Here's a simple RC circuit with R=1kΩ and C=10µF:

[Syntax-highlighted Python code block displayed once]
```

## Ralph Integration

For future duplication issues, Ralph Fixer should:

1. **Categorize:** `response_duplication` as `likely_code_bug` (display logic issue)
2. **Recommend:** "Check st.write() and st.code() calls - ensure code not displayed twice"
3. **Fix strategy:** `code_review` (manual fix required)

**Potential Ralph enhancement:**
```python
elif issue_type == 'response_duplication':
    analysis['root_cause'] = 'UI display logic duplicating content'
    analysis['recommendation'] = 'Review st.write() and st.code() usage - parse and display separately'
    analysis['fix_strategy'] = 'code_review'
    analysis['category'] = 'likely_code_bug'
```

## Files Modified

1. **app.py** - Fixed duplication by parsing response before display
2. **app_logger.py** - Added `log_response_duplication()` function

## Related Issues

- This fix eliminates one source of repetition, but the LLM itself might still generate duplicate code blocks (separate issue)
- If LLM generates duplicate code blocks, add parsing logic to deduplicate: `code = list(set(code_blocks))[0]` after extraction

---

**Status:** ✅ Fixed - Response duplication eliminated
**Date:** 2026-02-16
**Reporter:** Augusto (Telegram)
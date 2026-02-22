# Issue Chain Analysis Report

**Date:** 2026-02-22
**Purpose:** Determine root causes of recent issues - LLM-related vs Code Bugs

---

## Executive Summary

**Key Finding: Issues are being MISLABELED as LLM issues when many are likely CODE BUGS**

The current system categorizes most failures as "empty_output" or "simulation_error" without distinguishing between:
- Actual LLM generation problems
- Code bugs in our validation logic
- Code bugs in data extraction logic
- Code bugs in simulation execution

---

## Issues Analyzed (10 most recent)

### Pattern: Same prompt failing repeatedly

**Prompt:** "Simulate a low-pass filter with cutoff 1kHz using R=1.59kOhm and C=100nF"

**Occurrences:**
- 2026-02-18 20:09:47 - Model: cogito-2.1:671b - empty_output
- 2026-02-18 20:11:53 - Model: glm-4.7 - simulation_error
- 2026-02-18 20:20:12 - Model: cogito-2.1:671b - empty_output
- 2026-02-18 20:22:50 - Model: glm-4.7 - simulation_error
- 2026-02-18 20:35:07 - Model: glm-4.7 - empty_output

**This pattern suggests:**

1. **NOT a single LLM issue** - Multiple models failing on same prompt
2. **Possibly a code bug** - Same exact prompt failing consistently
3. **Validation or extraction failing** - Code runs but no data

---

## Root Cause Analysis by Issue Type

### 1. empty_output Issues

**Context:** "Simulation produced no data"

**What actually happens:**
1. LLM generates code (non-empty response)
2. Code executes successfully (no exception)
3. Validation passes
4. `results['data']` is empty (0 data points)

**Possible causes:**

#### Cause A: Code Bug - Validation Too Weak
**Evidence:** `validate_circuit_code()` only checks string matches
```python
# Current validation (WEAK!)
if 'analysis' not in code:
    return False, "Missing required element: analysis"
```

This passes for:
```python
# BAD: analysis is mentioned but not assigned
analysis = None
# or
# analysis # (comment)
```

**Should be:**
- Check if `analysis` is actually ASSIGNED
- Check if `analysis` has the right type
- Check if analysis is created from `simulator.transient()` or `simulator.ac()`

#### Cause B: Code Bug - Extraction Failed
**Evidence:** `_extract_analysis_data()` may fail silently

Code path:
1. `analysis` object exists
2. `analysis.time` may not exist
3. `analysis.nodes` may not exist
4. Loop tries to find variables
5. Returns empty list if nothing found

**Possible issues:**
- Wrong node names (LLM used 'output' but we look for 'out')
- Bracket notation not working
- Analysis type mismatch (AC analysis when expecting transient)

#### Cause C: LLM Issue - Missing Code
**Evidence:** LLM might generate incomplete code

But this would likely cause a SyntaxError before the data check.

---

### 2. simulation_error - "Missing required element: analysis"

**Evidence:** This error comes from our validation

**Root Cause: CODE BUG**

`validate_circuit_code()` checks:
```python
required_elements = ['circuit', 'Circuit(', 'analysis']
```

This is STRING MATCHING, not runtime validation!

**Example passes validation:**
```python
# Passes validation BUT has no actual analysis
circuit = Circuit()
# TODO: create analysis
```

**Example fails validation:**
```python
# Fails validation even though it's correct
cir = Circuit()  # Name is 'cir' not 'circuit'
analysis = simulator.transient(...)
```

**Fix Required:** The validation checks strings AFTER code would run, but it should check BEFORE:
- Look for assignment patterns: `analysis = `
- Look for method calls: `.transient(`, `.ac(`
- Don't rely on specific variable names

---

### 3. simulation_error - "Unknown argument pulse=(...)"

**Error:** `Unknown argument pulse=(0, 5, 0, PeriodValue(1 μs), PeriodValue(1 μs), PeriodValue(0.5 ms), PeriodValue(1 ms))`

**Root Cause: CODE BUG + LLM Issue**

**LLM Issue:** Generated wrong syntax for `PulseVoltageSource`
- LLM used positional arguments with strange tuple

**Code Bug:** Our auto-convert DC→Pulse might have created this format

**But:** Looking at the code, our PulseVoltageSource generates:
```python
circuit.PulseVoltageSource(
    'name', node_plus, node_minus,
    initial_value=0 @ u_V,
    pulsed_value=target @ u_V,
    ...
)
```

This looks correct. So the LLM generated the bad format directly.

---

## Test Coverage Gaps

### Missing Tests

1. **No integration test for end-to-end flow:**
   - LLM prompt → Code generation → Validation → Simulation → Data extraction

2. **No test for validation logic:**
   - Should fail on bad code
   - Should pass on good code
   - Currently only tests on real code

3. **No test for data extraction:**
   - What happens when analysis.time exists?
   - What happens when analysis.frequency exists?
   - What happens when node names don't match?

4. **No test for edge cases:**
   - AC analysis vs transient analysis
   - Multiple nodes vs single node
   - Different node naming conventions

---

## Recommendations

### Immediate Actions (Priority 1)

1. **Fix validate_circuit_code() to check for ACTUAL analysis**
   ```python
   # Check for analysis assignment pattern
   def validate_circuit_code(code):
       # Look for pattern: analysis = simulator.transient(...)
       if not re.search(r'analysis\s*=\s*\w+\.simulator\(\)\.(transient|ac)\(', code):
           return False, "Missing analysis assignment (analysis = simulator.transient(...))"

       # Check for transient or AC call
       if '.transient(' not in code and '.ac(' not in code:
           return False, "Missing simulation method (.transient() or .ac())"

       return True, None
   ```

2. **Add debug logging when empty_output occurs**
   ```python
   elif not results.get('data') or len(results['data']) == 0:
       # Log with MORE debugging info
       log_empty(
           prompt=user_input,
           llm_model=...,
           provider=...,
           context=f"Simulation produced no data. Analysis type: {type(analysis)}. Has time: {hasattr(analysis, 'time')}. Has nodes: {hasattr(analysis, 'nodes')}"
       )
   ```

3. **Add detailed debug output to circuit_builder.py**
   - Log `filtered_code` after all fixes
   - Log `analysis` object attributes
   - Log extraction attempts and failures

4. **Create integration test**
   - Use same low-pass filter prompt that's failing
   - Run through complete chain
   - Capture each stage: prompt → LLM code → filtered code → analysis → data

### Medium Priority

5. **Improve issue categorization**
   - Add `CODE_BUG` type
   - Add `EXTRACTION_FAILURE` type
   - Auto-detect code bugs vs LLM issues

6. **Add unit tests for _extract_analysis_data**
   - Test with mock analysis objects
   - Test different node structures
   - Test edge cases

7. **Visual debugging in UI**
   - Show filtered_code to user
   - Show analysis time range
   - Show what variables were found

### Long Term

8. **Run Ralph Fixer with code bug detection**
   - Only improve prompts for actual LLM issues
   - Fix code bugs separately
   - Track which category each fix belongs to

---

## Next Steps

1. **Add debug logging to understand empty_output root cause**
   - Modify app.py to log more details when data is empty
   - Run the low-pass filter prompt again
   - Check logs to see where the chain breaks

2. **Fix validate_circuit_code()**
   - Make it check for actual assignment, not string match
   - Test it with good and bad code examples

3. **Create integration test**
   - Standalone script that runs low-pass filter
   - Captures all intermediate states
   - Can be run in VS Code with breakpoints

---

**Conclusion:**
Most recent issues labeled as "empty_output" and "simulation_error" are likely **CODE BUGS** in validation/extraction logic, not LLM issues. Fixing these bugs should significantly reduce the issue count. Ralph Fixer should focus on LLM issues only.

**Action:** Add debug logging to trace the exact failure point before running Ralph Fixer.
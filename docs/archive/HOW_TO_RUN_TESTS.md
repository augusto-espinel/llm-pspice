# Run My Exact Tests - Here's How

## Quick Start

Double-click this file or run:
```powershell
start_tests.bat
```

This will:
1. Explain what the tests do
2. Run both tests
3. Show you the complete results

## What You'll See

### Step 1: Summary

The tests will explain:
- What the problem was (wrong pulse syntax)
- What I fixed (system prompt)
- What each test proves
- How to interpret results

### Step 2: Test 1 - Direct LLM Test

```
TEST 1: Direct LLM Test
Testing: cogito-2.1:671b (cloud)
Prompt: Simulate a low-pass filter with cutoff 1kHz using R=1.59kOhm and C=100nF
Waiting for LLM response (30-90 seconds)...

ANALYSIS:
  Has PulseVoltageSource: True     ← EXPECT THIS
  Has WRONG pulse syntax: False    ← EXPECT THIS
  Has .transient(): True           ← EXPECT THIS

VERDICT: SUCCESS!
```

### Step 3: Test 2 - Streamlit-Style Test

```
TEST 2: Streamlit-Style Test
Testing: exact same code path as Streamlit app

ANALYSIS:
[1] Has Python code block: True      ← Should be True
[2] Has PulseVoltageSource: True     ← Should be True
[3] Has WRONG pulse syntax: False    ← Should be False
[4] Has .transient(): True           ← Should be True
[5] Has circuit = Circuit(: True     ← Should be True

FINAL VERDICT: PASS! All checks successful.
```

## Understanding the Results

### If BOTH Tests PASS

This means:
- ✅ `llm_orchestrator.py` has the improved system prompt
- ✅ Fresh Python processes use the correct code
- ✅ LLM generates right `PulseVoltageSource` syntax

**If your Streamlit still fails:**
- Your Streamlit is using OLD cached code
- Solution: Find the terminal running Streamlit, press **Ctrl+C**, then restart

### If Tests FAIL

This means:
- ❌ `llm_orchestrator.py` not updated
- ❌ File caching issue
- ❌ Wrong file being loaded

**Solutions:**
```powershell
# 1. Check file has pulse source example
type llm_orchestrator.py | findstr /i "PulseVoltageSource"

# 2. Delete cached Python files
del /s "*.pyc"
del /s "__pycache__"

# 3. Try from fresh terminal
```

## What's in Each File

| File | Purpose |
|------|---------|
| `test_llm_direct.py` | My first test - direct LLM call |
| `test_like_streamlit.py` | My second test - exact Streamlit code path |
| `test_summary.py` | Explains what each test proves |
| `run_all_tests.bat` | Runs both tests and saves output |
| `start_tests.bat` | Shows summary, then runs tests |
| `TEST_SUITE_README.md` | Detailed documentation |

## Quick Reference

**Run tests:** `start_tests.bat`

**Check results:**
- `test_1_response.txt` - Full LLM output from test 1
- `streamlit_response.txt` - Full LLM output from test 2

**Look for in responses:**
```python
# CORRECT (what you should see):
circuit.PulseVoltageSource('input', 'in', circuit.gnd,
    initial_value=0 @ u_V,
    pulsed_value=10 @ u_V,
    ...

# WRONG (what your Streamlit was showing):
circuit.V('input', 'n1', 'n2', pulse=(0, 5, 0, PeriodValue(...)))
```

## Why I Made These Tests

I needed to prove that:
1. My code fix works (test_llm_direct.py proves this)
2. Streamlit code path works (test_like_streamlit.py proves this)
3. Your Streamlit app issue is old cached code (if tests pass but Streamlit fails)

## What to Send Me

After running the tests, send me:
1. Test output (screenshots or text)
2. The generated response files:
   - `test_1_response.txt`
   - `streamlit_response.txt`

I can then tell you exactly what's happening and how to fix it!

## Time Required

Each test takes 30-90 seconds (LLM API call time).
Total: ~2-3 minutes to run both tests.

## Prerequisites

```powershell
conda activate pyspice
cd llm-sim-poc
```

Must have:
- pyspice conda environment
- Ollama Cloud API key saved
- Internet connection

---

**Ready? Double-click `start_tests.bat` to begin!**
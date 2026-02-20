# Manual Testing Guide for LLM-Generated Circuit Code

## Overview

You can independently test circuit code from the llm-pspice app using VS Code without running the Streamlit UI. This helps debug issues and verify code correctness.

## Pre-Requisites

### 1. Activate the PySpice Environment

```powershell
conda activate pyspice
```

If that fails, create it:
```powershell
conda create -n pyspice python=3.10
conda activate pyspice
pip install PySpice matplotlib pandas
```

### 2. Verify Your Setup

```powershell
python verify_setup.py
```

You should see:
```
Testing PySpice Setup...
[1] Testing PySpice imports... OK
[2] Building test circuit... OK
[3] Running simulation... OK
[4] Checking results... OK
    Time points: 50001
    Time range: 0.000000 to 0.005000 s

SUCCESS: PySpice setup is working correctly!
```

## Method 1: Automated Testing (Recommended)

### Step 1: Get LLM Code

From the llm-pspice app, copy the generated Python code block:

```python
# Paste this into standalone_test.py
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('RC_Filter')
# ... rest of code
```

### Step 2: Paste Into Test Script

Open `standalone_test.py` in VS Code:

```powershell
code standalone_test.py
```

Find line 37 and paste your code:

```python
CIRCUIT_CODE = """
# PASTE YOUR CODE HERE
"""
```

### Step 3: Run Test

```powershell
python standalone_test.py
```

### Reading the Output

**SUCCESS:**
```
[1/5] Checking Python syntax... OK
[2/5] Checking PySpice imports... OK
[3/5] Validating PySpice units... OK
[4/5] Creating circuit object... OK
[5/5] Checking simulation results... OK
    Time points: 100001

RESULT: ALL CHECKS PASSED ✅
```

**AUTO-FIXED:**
```
[3/5] Validating PySpice units...
    VALIDATION: FAILED (before fixes)
    Auto-applied fixes to code
    VALIDATION: OK (after fixes)
```

**FAILED:**
```
[4/5] Creating circuit object... FAILED
    Singular matrix: check connections
```
→ Fix: Add DC path to ground for all nodes

## Method 2: VS Code Debug Mode

### Step 1: Open Test File

```powershell
code standalone_test.py
```

### Step 2: Set Breakpoints

- Click in the left margin next to line 105 (after execution)
- Or press F9 on that line

### Step 3: Start Debugging

- Press F5
- Select "Python File"

### Step 4: Inspect Variables

In the **Variables** panel (left side), check:

| Variable | What to Check |
|----------|---------------|
| `namespace` | Should contain `circuit` and `analysis` keys |
| `namespace['circuit']` | Should be a Circuit object |
| `namespace['analysis']` | Should have `time`, `n1`, `n2` attributes |
| `analysis.time` | Should have length > 0 |

### Step 5: Step Through Code

- F10: Step over (execute current line)
- F11: Step into (go into functions)
- Shift+F11: Step out (exit current function)
- F5: Continue (run to next breakpoint)

## Method 3: Manual Test File

Create your own test file:

```powershell
code my_test.py
```

Paste this template:

```python
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

# === PASTE LLM CODE HERE ===
circuit = Circuit('My_Circuit')
# ... rest of LLM code
# === END LLM CODE ===

# Manual checks
print(f"Circuit created: {circuit}")
print(f"Has simulation: {'analysis' in locals() or 'analysis' in globals()}")

if 'analysis' in locals() or 'analysis' in globals():
    analysis = locals().get('analysis') or globals().get('analysis')
    print(f"Time points: {len(analysis.time)}")
    print(f"Data shape: {analysis.time.shape}")
```

Run:
```powershell
python my_test.py
```

## Common Issues and Solutions

### Issue 1: "ModuleNotFoundError: PySpice"

**Cause:** Not in the pyspice conda environment

**Fix:**
```powershell
conda activate pyspice
python verify_setup.py
```

### Issue 2: "name 'u_uF' is not defined"

**Cause:** Invalid PySpice unit (doesn't exist)

**Fix:**
The automated script (`standalone_test.py`) auto-fixes this:
- `u_uF` → `u_nF`
- `u_MOhm` → `u_kOhm

**Manual fix:**
```python
# Replace
circuit.C(1, 'n2', 'gnd', 10 @ u_uF)  # Wrong

# With
circuit.C(1, 'n2', 'gnd', 10 @ u_nF)  # Correct
```

### Issue 3: "singular matrix: check connections"

**Cause:** Node doesn't have a DC path to ground

**Fix:**
```python
# Wrong - circuit is floating
circuit.R(1, 'n1', 'n2', 1 @ u_kOhm)
circuit.C(1, 'n2', 'n3', 10 @ u_nF)

# Right - all nodes connect to ground
circuit.R(1, 'n1', circuit.gnd, 1 @ u_kOhm)
circuit.C(1, 'n1', circuit.gnd, 10 @ u_nF)
```

### Issue 4: Simulation has no data

**Cause:** Using DC source in transient analysis

**Fix:**
```python
# Wrong - hides transient behavior
circuit.V('input', 'n1', 'gnd', 10 @ u_V)

# Right - shows charging behavior
circuit.PulseVoltageSource(
    'input', 'n1', 'gnd',
    initial_value=0 @ u_V,
    pulsed_value=10 @ u_V,
    pulse_width=100 @ u_ms,
    period=100 @ u_ms,
    delay_time=0.001 @ u_ms,
    rise_time=0.001 @ u_ms
)
```

## Debugging Checklist

Before moving forward, verify each step:

- [ ] **Conda environment active**: `conda activate pyspice`
- [ ] **PySpice installed**: `pip show PySpice`
- [ ] **Setup verified**: `python verify_setup.py` passes
- [ ] **Code pasted into**: `standalone_test.py` (line 37)
- [ ] **Test runs**: `python standalone_test.py`
- [ ] **Check 1-5 pass**: All OK
- [ ] **Check 5 critical**: Analysis has data points

## VS Code Tips

### Useful Extensions

1. **Python** (Microsoft) - Python language support
2. **Pylance** - Code intelligence
3. **Jupyter** - For interactive notebooks

### Keyboard Shortcuts

- `Ctrl+Shift+P`: Command palette
- `F5`: Start debugging
- `F9`: Toggle breakpoint
- `Ctrl+``: Toggle terminal

### Launch Configuration

Create `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": false
        }
    ]
}
```

## Workflow Summary

```
llm-pspice app
    ↓ (generate code)
Copy code
    ↓
Paste into standalone_test.py
    ↓
python standalone_test.py
    ↓
Check results
    ↓
✅ PASS → Code is good, use in app
❌ FAIL → Fix errors, re-test
```

## Example: Full Test Session

```powershell
# 1. Activate environment
conda activate pyspice

# 2. Verify setup
python verify_setup.py

# 3. Open test file (in VS Code) and paste code
code standalone_test.py

# 4. Run test
python standalone_test.py

# 5. If pass, you're done!
# If fail, read the error message and fix the code
```

## Quick Commands Cheat Sheet

```powershell
# Environment setup
conda activate pyspice

# Verify everything works
python verify_setup.py

# Run automated test
python standalone_test.py

# Open in VS Code
code standalone_test.py

# Find PySpice location
pip show PySpice | findstr Location

# Check PySpice version
pip show PySpice
```

## Files You'll Use

| File | Purpose |
|------|---------|
| `verify_setup.py` | Check your PySpice installation |
| `standalone_test.py` | Automated 5-step validation |
| `VSCODE_TESTING_GUIDE.md` | Full detailed guide |
| `VSCODE_QUICK_REFERENCE.md` | Quick reference card |

## Need Help?

1. Check error messages - they're descriptive
2. Read `VSCODE_QUICK_REFERENCE.md` for common fixes
3. Run `verify_setup.py` to check installation
4. Use VS Code debug mode to inspect variables step-by-step
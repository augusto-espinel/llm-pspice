# LLM Code Fixes in circuit_builder.py

## Date: 2026-02-22

## Overview
Added automatic fixes for common LLM-generated code errors in PySpice circuit simulations.

## Fixes Implemented

### 1. Sinusoidal Source Syntax Error (Line ~265)
**Problem:** LLM generates `circuit.Sinusoidal()` which doesn't exist in PySpice
**Example:** `circuit.Sinusoidal('input', 'in', circuit.gnd, amplitude=1@u_V)`
**Fix:** Replace with `circuit.SinusoidalVoltageSource()`
```python
filtered_code = re.sub(r'circuit\.Sinusoidal\(', 'circuit.SinusoidalVoltageSource(', filtered_code)
```

### 2. Python Keyword Node Names (Line ~278)
**Problem:** LLM uses Python keywords like 'in' as node names, causing errors
**Example:** `circuit.R(1, 'in', 'out', 1.59 @ u_kOhm)`
**Fix:** Replace 'in' with 'input_node'
```python
filtered_code = re.sub(r"'in'", "'input_node'", filtered_code)
filtered_code = re.sub(r'"in"', '"input_node"', filtered_code)
```

## Existing Fixes (Previously Implemented)

### Unit Typos (Line ~257)
**Fix:** u_uF → u_nF, u_MOhm → u_kOhm, etc.

### DC to Pulse Conversion (Line ~250)
**Fix:** DC sources → PulseVoltageSource for transient analysis

### Import Filtering (Line ~246)
**Fix:** Remove duplicate PySpice imports

## Testing
- Tested regex patterns work correctly
- Verified simulation runs successfully with fixes
- Generated 501 data points for low-pass filter test

## Files Modified
- `C:\Users\augus\.openclaw\workspace\llm-sim-poc\circuit_builder.py`

## Impact
These fixes increase reliability of LLM-generated PySpice code by automatically correcting common syntax errors before simulation.
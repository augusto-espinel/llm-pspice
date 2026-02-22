# RC Circuit Benchmark for LLM-PSPICE Testing

## Overview

This benchmark provides a **pure Python, analytical solution** for RC circuits that serves as a **ground truth reference** to validate PySpice simulations. Ralph can use this to test and improve the LLM-PSPICE app until it generates comparable results.

## Why This Benchmark?

**Problem:** PySpice simulations may have numerical errors, discretization issues, or incorrect parameters.

**Solution:** Use analytical differential equations (exact math) to verify simulation accuracy.

**Goal:** LLM-PSPICE app should generate PySpice code that produces results within **5% tolerance** of this benchmark.

---

## Files

1. **`benchmark_rc_circuit.py`** - Pure Python analytical RC circuit calculator
   - No PySpice dependency
   - Exact solutions using differential equations
   - Charging/discharging/AC responses
   - Comparison metrics

2. **`test_benchmark.py`** - Test script to validate PySpice vs benchmark
   - Runs PySpice simulation
   - Compares with analytical solution
   - Generates comparison plots
   - Reports pass/fail status

3. **`BENCHMARK_README.md`** - This file (how to use)

---

## Quick Start

### 1. Run the Benchmark (Analytical Solution)

```bash
python benchmark_rc_circuit.py
```

This generates:
- Analytical voltage and current data
- Comparison plot with sample simulation
- `benchmark_data.npz` - saved data for comparison
- Test case description for Ralph

### 2. Run the Validation Test

```bash
python test_benchmark.py
```

This:
- Runs PySpice simulation for RC circuit
- Compares with analytical benchmark
- Generates comparison plots
- Reports pass/fail within 5% tolerance

---

## Test Case for Ralph

**Circuit:** RC low-pass filter (charging/step response)

**Parameters:**
```
R = 1000 Ohms (1 kOhm)
C = 10 microfarads (10 µF)
Vin = 10 Volts (step input at t=0)
```

**Simulation:**
```
Type: Transient analysis
Step time: 1 ms (10% of time constant)
End time: 50 ms (5 time constants)
```

**Expected Results (Analytical Benchmark):**
```
Time constant (τ): 10 ms
Final voltage: ~9.93 V (99.3% of Vin)
Final current: ~0 mA
Cutoff frequency: ~15.9 Hz
```

---

## Success Criteria

PySpice simulation from LLM-PSPICE app should meet:

1. **Voltage Error**: < 5% relative error compared to benchmark
2. **Current Error**: < 5% relative error compared to benchmark
3. **Time Constant**: Accurate within 5%
4. **Pass Rate**: ≥ 95% of data points within tolerance

---

## How Ralph Should Use This

### Step 1: Generate PySpice Code

Use LLM-PSPICE app to create circuit code. The prompt should be:

```
Design an RC low-pass filter circuit with 1 kOhm resistor and 10 µF capacitor.
Apply a 10V step input. Run transient analysis.
```

**Expected PySpice code:**
```python
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('RC_LowPass_Filter')
circuit.V('input', 'n1', circuit.gnd, 10 @ u_V)
circuit.R(1, 'n1', 'n2', 1 @ u_kOhm)
circuit.C(1, 'n2', circuit.gnd, 10 @ u_F)

simulator = circuit.simulator()
analysis = simulator.transient(
    step_time=1 @ u_ms,
    end_time=50 @ u_ms
)
```

### Step 2: Run Test Benchmark

```bash
python test_benchmark.py
```

This compares LLM-PSPICE output with analytical benchmark.

### Step 3: Check Results

**✓ PASS** (if all criteria met):
- Error < 5%
- Pass rate ≥ 95%
- Results match theoretical expectations

**✗ FAIL** (if any criteria not met):
- Analyze error patterns
- Identify what's wrong with generated code
- Improve LLM prompt or code generation

### Step 4: Iterate Until Success

If test fails:

1. **Check PySpice code:**
   - Are component values correct?
   - Is simulation time appropriate (5τ)?
   - Are annotations correct (@ u_V, @ u_Ohm)?

2. **Check circuit topology:**
   - Is the RC series connection correct?
   - Is ground properly defined?

3. **Check simulation parameters:**
   - Step time small enough for resolution?
   - End time long enough for steady state?

4. **Debug with plots:**
   - Compare plots visually
   - Look for obvious discrepancies
   - Check steady-state values

Repeat until test passes with < 5% error.

---

## Benchmark Mathematics

### Charging Response (Step Input)

**Differential Equation:**
```
RC * dVc/dt + Vc = Vin
```

**Solution:**
```
Vc(t) = Vin * (1 - exp(-t/τ))
I(t) = (Vin/R) * exp(-t/τ)
```

Where τ = R * C (time constant)

### Discharging Response

**Differential Equation:**
```
RC * dVc/dt + Vc = 0
```

**Solution:**
```
Vc(t) = V0 * exp(-t/τ)
I(t) = -(V0/R) * exp(-t/τ)
```

---

## Comparison Metrics

The test script calculates:

- **Max Absolute Error**: Maximum voltage difference (V)
- **Max Relative Error**: Maximum percentage error (%)
- **Mean Absolute Error**: Average voltage difference (V)
- **Mean Relative Error**: Average percentage error (%)
- **RMS Error**: Root-mean-square voltage difference (V)
- **Pass Rate**: Percentage of points within tolerance (%)

---

## Example Output

```
TEST 1: RC Charging Circuit (Step Response)

Circuit:
  R = 1000 Ohms
  C = 10.0 uF
  Vin = 10 V

Results:
  Final voltage (benchmark): 9.9326 V
  Final voltage (PySpice): 9.9312 V
  Final current (benchmark): 0.0067 mA
  Final current (PySpice): 0.0068 mA

Comparison Metrics:
  Max voltage error: 0.0123 V (1.24%)
  Mean voltage error: 0.0045 V (0.45%)
  RMS error: 0.0056 V
  Pass rate (within 5% tolerance): 98.2%

✓ TEST PASSED: PySpice results match benchmark within tolerance
```

---

## Common Issues & Solutions

| Issue | Symptoms | Solution |
|-------|----------|----------|
| Wrong time constant | Voltage rises too fast/slow | Check R and C values, ensure units correct |
| Incorrect steady state | Voltage doesn't reach expected | Check circuit topology, ground connection |
| Discretization errors | Jagged/wrong waveform | Reduce step time or increase simulation time |
| Wrong current direction | Current negative when should be positive | Check component connection order |
| Missing units | PySpice errors | Ensure @ u_V, @ u_Ohm annotations used |

---

## Extending the Benchmark

To add more test cases:

1. **Different RC values:** Create new test with different time constant
2. **AC analysis:** Test frequency response with `steady_state_ac_response()`
3. **Discharging:** Test capacitor discharge from initial voltage
4. **Series RC with source:** Test with AC or pulse input

---

## Integration with LLM-PSPICE App

**Ralph can integrate this by:**

1. **Add benchmark validation** as a post-simulation step
2. **Auto-compare** simulation results with analytical solution
3. **Flag errors** to user if results deviate > 5%
4. **Suggest fixes** based on error patterns
5. **Provide confidence score** for each simulation

---

## References

- **RC Circuit Theory:** Standard first-order circuit analysis
- **Differential Equations:** First-order linear ODE solutions
- **PySpice Documentation:** https://pyspice.fabrice-salvaire.fr/

---

**Status:** Ready for Ralph to use and test LLM-PSPICE accuracy!

---

**Author:** Benchmark framework for LLM-PSPICE validation
**Date:** 2026-02-14
# Test 2 Simulation Error Quick Reference

When running `test_like_streamlit_simulation.py`, you may encounter specific errors. This guide explains what they mean.

## Common Simulation Errors

### 1. "Missing required element: analysis"

**What it means:**
LLM generated circuit code but didn't include an analysis call (`.transient()` or `.ac()`)

**Example LLM output:**
```python
circuit = Circuit('test')
circuit.R(1, 'n1', 'n2', 1 @ u_kOhm)
circuit.C(1, 'n2', circuit.gnd, 100 @ u_nF)

# Missing: simulator = circuit.simulator()
# Missing: analysis = simulator.transient(step_time=1 @ u_ms, end_time=10 @ u_ms)
```

**Root cause:**
System prompt doesn't explicitly instruct to add analysis

**Fix:**
1. Check llm_orchestrator.py system prompt includes:
   ```
   Always include analysis:
   - For time-domain: simulator = circuit.simulator(); analysis = simulator.transient(...)
   - For frequency-domain: analysis = simulator.ac(...)
   ```

2. Test with prompt that explicitly asks for analysis:
   ```
   "Simulate low-pass filter and do transient analysis for 10ms"
   ```

---

### 2. "Simulation produced no data"

**What it means:**
Ngspice ran successfully but returned empty results

**Common causes:**
- Using DC source in transient analysis (shows steady-state only)
- Capacitor behaves as open circuit at DC (Z → ∞)
- No time points generated

**Example:**
```python
# WRONG for transient:
circuit.V('input', 'n1', 'n2', 10 @ u_V)  # DC source

# CircuitBuilder tries to auto-fix, but may fail if:
# - Can't detect transient analysis
# - Source format unexpected
```

**Root cause:**
DC source doesn't show charging behavior in transient analysis

**Fix (CircuitBuilder auto-fix):**
CircuitBuilder should convert DC to PulseVoltageSource automatically:
```python
# Auto-converted to:
circuit.PulseVoltageSource('input', 'n1', 'n2',
    initial_value=0 @ u_V,
    pulsed_value=10 @ u_V,
    pulse_width=100 @ u_ms,
    period=100 @ u_ms,
    ...)
```

**Manual fix in generated code:**
Use PulseVoltageSource directly instead of Circuit.V()

---

### 3. "ngspice exited with error code 1"

**What it means:**
Ngspice crashed during simulation

**Common errors:**

**a) Unit typos:**
```python
# WRONG:
circuit.C(1, 'n1', circuit.gnd, 100 @ u_uF)  # u_uF doesn't exist!
circuit.R(1, 'n1', 'n2', 1 @ u_MOhm)  # u_MOhm doesn't exist!

# CORRECT:
circuit.C(1, 'n1', circuit.gnd, 100 @ u_nF)  # nano-farads, not micro-micro
circuit.R(1, 'n1', 'n2', 1 @ u_kOhm)  # kilo-ohms, not mega
```

b) Syntax errors:
```python
# WRONG:
circuit.R(1, 'n1', 'n2', 1k @ u_Ohm)  # No space!
circuit.C(1, 'n1', 'n2', 100 @ nF)  # Missing u_ prefix!

# CORRECT:
circuit.R(1, 'n1', 'n2', 1 @ u_kOhm)
circuit.C(1, 'n1', 'n2', 100 @ u_nF)
```

**Fix:**
CircuitBuilder automatically fixes common typos (u_uF → u_nF). If not fixed, update unit_validator.py.

---

### 4. "duplicate declaration of struct ngcomplex"

**What it means:**
PySpice tried to initialize Ngspice twice

**Root cause:**
LLM-generated code includes import statements that reinitialize Ngspice

**Example:**
```python
# LLM generates:
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('test')
# ... more code

# This causes duplicate initialization because we already imported these!
```

**Fix:**
CircuitBuilder automatically filters out PySpice imports:
```python
# In circuit_builder.py:
filtered_code = self._filter_pyspice_imports(circuit_code)
# Removes lines like: from PySpice.Spice.Netlist import Circuit
```

If still failing, check generated code for hidden imports.

---

### 5. "No circuit defined"

**What it means:**
Code executed but `circuit` variable not created

**Root cause:**
LLM didn't generate circuit definition or used wrong variable name

**Example:**
```python
# WRONG:
sim = Circuit('test')  # Wrong variable name!

# CORRECT:
circuit = Circuit('test')  # Must be 'circuit' variable
```

**Fix:**
System prompt must instruct: "Create a variable named 'circuit' using Circuit()"

---

### 6. "Variable X not found"

**What it means:**
Circuit references undefined variable

**Example:**
```python
# WRONG:
circuit.R(1, Vin, Vout, Rval @ u_kOhm)  # Variables not defined!

# CORRECT:
Vin = 10  # Define first
Vout = 5
Rval = 1.59
circuit.R(1, 'Vin', 'Vout', Rval @ u_kOhm)  # Or use strings
```

**Fix:**
Code must define all variables before using them, or use string node names.

---

## Debugging Workflow

When Test 2 fails:

1. **Check generated code:**
   ```powershell
   type streamlit_response.txt
   ```

2. **Look for specific errors:**
   ```powershell
   type test_2_simulation_output.txt | findstr /i error
   ```

3. **Check simulation summary:**
   ```powershell
   type test_2_simulation_summary.json
   ```

4. **Identify stage:**
   - Code generation fails → Fix system prompt
   - Circuit build fails → Fix code extraction/validation
   - Simulation fails → Fix circuit code or simulation parameters

---

## Comparing Test 2 to Streamlit

When Test 2 fails, check if it matches your Streamlit errors:

| Test 2 Error | Streamlit Error | Same Issue? |
|--------------|----------------|-------------|
| "Missing required element: analysis" | "Missing required element: analysis" | ✅ Same |
| "Simulation produced no data" | "Simulation produced no data" | ✅ Same |
| "ngspice exited with error" | "ngspice crashed" | ✅ Same |
| "Unit typos" | "Unit errors" | ✅ Same |

If Test 2 errors match your Streamlit errors:
- ✅ Test correctly replicates the issue
- ✅ You can debug independently of Streamlit
- ✅ Fix will apply to both

If Test 2 works but Streamlit fails:
- ❌ Streamlit is using cached code/state
- ✅ Fix: Properly restart Streamlit (Ctrl+C, then restart)

---

## Next Steps After Finding Error

1. **Identify error type** from this guide
2. **Check generated code** in streamlit_response.txt
3. **Apply appropriate fix:**
   - System prompt update (code generation issues)
   - CircuitBuilder fix (unit typos, imports)
   - ngspice debugging (simulation issues)
4. **Re-run Test 2** to verify fix works
5. **Streamlit benefits** once fix confirmed

This guide helps you quickly identify and fix simulation errors!
# Independent Circuit Testing with VS Code

## Quick Start: 3-Step Process

### Step 1: Get the LLM-generated code
When you get a response from the llm-pspice app, copy just the Python code block:
```python
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('RC_Filter')
...
```

### Step 2: Run standalone test
```powershell
cd llm-sim-poc
python standalone_test.py
```

This will automatically:
- ✅ Check Python syntax
- ✅ Validate PySpice imports
- ✅ Fix common unit typos (u_uF -> u_nF, etc.)
- ✅ Execute the circuit definition
- ✅ Run the simulation
- ✅ Check if results were produced

### Step 3: Read the output
```
[1/5] Checking Python syntax... OK
[2/5] Checking PySpice imports... OK
[3/5] Validating PySpice units... OK
[4/5] Creating circuit object... OK
[5/5] Checking simulation results... OK

RESULT: ALL CHECKS PASSED
```

## VS Code Debugging Steps

### 1. Set up the conda environment
```powershell
# Make sure you're in the pyspice conda environment
conda activate pyspice

# Verify PySpice is installed
pip show PySpice
```

### 2. Open standalone_test.py in VS Code
```powershell
code standalone_test.py
```

### 3. Edit the CIRCUIT_CODE section
Find the section marked with:
```python
# ========================================
# STEP 1: Paste LLM-generated code here
# ========================================
CIRCUIT_CODE = """
"""
```

Paste your code between the triple quotes.

### 4. Run with debugging
1. Press F5 or click "Run and Debug"
2. Select "Python File"
3. Set breakpoints if needed

**Key variables to inspect:**
- `namespace['circuit']` - The circuit object
- `namespace['analysis']` - Simulation results
- `analysis.time` - Time axis points
- `analysis.n1`, `analysis.n2` - Node voltages

## Common Errors and Fixes

### Error 1: ModuleNotFoundError
```
ModuleNotFoundError: No module named 'PySpice'
```
**Fix:**
```powershell
conda activate pyspice
pip install PySpice
```

### Error 2: name 'u_uF' is not defined
```
NameError: name 'u_uF' is not defined
```
**Fix:**
The standalone_test.py script will auto-fix this:
- `u_uF` → `u_nF`
- `u_MOhm` → `u_kOhm`

### Error 3: singular matrix
```
Singular matrix: check connections
```
**Fix:**
Add a DC path to ground for every node:
```python
# WRONG - floating node
circuit.R(1, 'n1', 'n2', 1 @ u_kOhm)
circuit.C(1, 'n2', 'n3', 10 @ u_nF)

# RIGHT - all nodes connect to ground
circuit.R(1, 'n1', circuit.gnd, 1 @ u_kOhm)
circuit.C(1, 'n1', circuit.gnd, 10 @ u_nF)
```

### Error 4: Simulation produces no data
```
[5/5] Checking simulation results... WARNING - No node data found
```
**Common causes:**
1. DC source used in transient analysis (should use PulseVoltageSource)
2. Wrong simulation parameters (step_time or end_time too small)
3. Missing `analysis` variable assignment

**Fix for DC source:**
```python
# WRONG - hides transient behavior
circuit.V('input', 'n1', circuit.gnd, 10 @ u_V)

# RIGHT - shows charging behavior
circuit.PulseVoltageSource(
    'input', 'n1', circuit.gnd,
    initial_value=0 @ u_V,
    pulsed_value=10 @ u_V,
    pulse_width=100 @ u_ms,
    period=100 @ u_ms,
    delay_time=0.001 @ u_ms,
    rise_time=0.001 @ u_ms
)
```

## Manual Testing (Without Automated Script)

If you prefer to test completely manually:

### 1. Create test file
Create `manual_test.py`:
```python
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

# Paste LLM code here
circuit = Circuit('Test')
...

 simulator = circuit.simulator()
analysis = simulator.transient(...)

# Manually check
print(f"Circuit created: {circuit}")
print(f"Analysis time points: {len(analysis.time)}")
print(f"Time range: {analysis.time[0]} to {analysis.time[-1]}")
```

### 2. Run in VS Code
```powershell
python manual_test.py
```

### 3. Inspect results in debug mode
- Add breakpoint after simulation
- View `analysis` variable in Variables panel
- Check if `analysis.time` has data points

## Full Example Test

Copy this complete example to verify your setup:

```python
# RC low-pass filter (known working example)
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('RC_Filter')

# Pulse source for transient response
circuit.PulseVoltageSource(
    'input', 'n1', circuit.gnd,
    initial_value=0 @ u_V,
    pulsed_value=10 @ u_V,
    pulse_width=100 @ u_ms,
    period=100 @ u_ms,
    delay_time=0.001 @ u_ms,
    rise_time=0.001 @ u_ms
)

circuit.R(1, 'n1', 'n2', 1 @ u_kOhm)
circuit.C(1, 'n2', circuit.gnd, 10 @ u_nF)

simulator = circuit.simulator()
analysis = simulator.transient(step_time=0.1 @ u_us, end_time=10 @ u_ms)

print(f"Test passed: {len(analysis.time)} time points generated")
```

## Integration with llm-pspice Workflow

1. **Generate code** in llm-pspice app
2. **Copy code** from the app's code block
3. **Paste** into `standalone_test.py`
4. **Run test** to verify it works
5. **Fix any errors** found
6. **Copy fixed code** back to llm-pspice app if needed

This approach lets you debug independently of the Streamlit app!
# Fix for "Duplicate Declaration of struct ngcomplex" Error

## Problem

When running llm-pspice simulations, you might see:

```
❌ Simulation error: <cdef source string>:7: duplicate declaration of struct ngcomplex
```

## Root Cause

This error occurs when **PySpice is initialized multiple times** in the same Python process. This happens because:

1. The LLM generates code with import statements:
   ```python
   from PySpice.Spice.Netlist import Circuit
   from PySpice.Unit import *
   ```

2. When we execute this code multiple times (multiple simulations), PySpice tries to re-initialize its Ngspice backend

3. Ngspice doesn't support re-initialization and throws the duplicate declaration error

## Solution Implemented

### 1. Import Filtering

The code now **automatically filters out PySpice import statements** from LLM-generated code:

```python
def _filter_pyspice_imports(self, code):
    """Remove PySpice imports to prevent re-initialization"""
    import re

    import_patterns = [
        r'^\s*from PySpice[^#]*$',
        r'^\s*import PySpice[^#]*$',
        r'^\s*from pyspice[^#]*$',
        r'^\s*import pyspice[^#]*$',
    ]

    lines = code.split('\n')
    filtered_lines = []

    for line in lines:
        is_import = False
        for pattern in import_patterns:
            if re.match(pattern, line.strip(), re.IGNORECASE):
                is_import = True
                break

        if not is_import:
            filtered_lines.append(line)

    return '\n'.join(filtered_lines)
```

### 2. Pre-Loaded Namespace

Instead of executing imports, we provide PySpice objects in a **pre-loaded namespace**:

```python
namespace = {
    'Circuit': Circuit,           # Already imported
    'u_kOhm': u_kOhm,             # Unit: kilohm
    'u_V': u_V,                   # Unit: volt
    'u_ms': u_ms,                 # Unit: millisecond
    # ... more units
    'circuit': None,
    'analysis': None,
    'simulator': None
}
```

### 3. Better Error Handling

If the still occurs, we provide a clear error message:

```
❌ PySpice initialization error!

This happens when the LLM-generated code includes PySpice import statements.
The code has been filtered, but an error still occurred.

Technical error: duplicate declaration of struct ngcomplex

Try:
1. Refreshing the page and trying again
2. Using a simpler circuit description
```

## What Gets Filtered

The following lines are removed from LLM code:

```python
# ❌ These get removed:
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
import PySpice
from PySpice import *
from pyspice.Netlist import Circuit

# ✅ These stay:
circuit = Circuit('My_Circuit')
circuit.V('input', 'n1', circuit.gnd, 5 @ u_V)
# Comments
# Blank lines
# Other Python code
```

## Example

### Before Fix

**LLM generates:**
```python
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('RC_Filter')
circuit.V('input', 'n1', circuit.gnd, 5 @ u_V)
circuit.R(1, 'n1', 'out', 1 @ u_kOhm)
circuit.C(1, 'out', circuit.gnd, 10 @ u_nF)

simulator = circuit.simulator()
analysis = simulator.transient(step_time=0.1 @ u_ms, end_time=5 @ u_ms)
```

**Result:** ❌ Error on second run

### After Fix

**Filtered code:**
```python
circuit = Circuit('RC_Filter')
circuit.V('input', 'n1', circuit.gnd, 5 @ u_V)
circuit.R(1, 'n1', 'out', 1 @ u_kOhm)
circuit.C(1, 'out', circuit.gnd', 10 @ u_nF)

simulator = circuit.simulator()
analysis = simulator.transient(step_time=0.1 @ u_ms, end_time=5 @ u_ms)
```

**Result:** ✅ Works every time

## Files Modified

- **circuit_builder.py**
  - Added `_filter_pyspice_imports()` method
  - Updated `run_simulation()` to use filtered code
  - Added better error handling
  - Expanded namespace with more units

## Debug Output

You'll now see when imports are filtered:

```
[FILTER] Removed PySpice import: from PySpice.Spice.Netlist import Circuit
[FILTER] Removed PySpice import: from PySpice.Unit import *
[FILTER] Removed PySpice import: from PySpice import *

=== DEBUG INFO ===
Analysis type: <class 'PySpice.RawFile'>
Time length: 51
...
```

## Troubleshooting

### Still Getting the Error?

If you still see "duplicate declaration of struct ngcomplex":

**Solution 1: Refresh the Streamlit App**
- The Python process needs to be restarted
- Click "Stop" then "Rerun" in Streamlit
- Or refresh the browser page

**Solution 2: Check for Multiple Circuit Definitions**
Some LLMs might generate:
```python
circuit = Circuit('Circuit1')
# ... components ...
circuit = Circuit('Circuit2')  # ← This causes issues
# ... more components ...
```

Rewrite to use a single circuit definition.

**Solution 3: Clear Session State**
```python
# In Streamlit sidebar, click "Clear Chat"
```

This resets the circuit and analysis variables.

## Technical Details

### Why This Happens

PySpice uses the **Ngspice** C library under the hood. When you import PySpice modules:

1. Python loads the C extension
2. Ngspice initializes its internal data structures
3. The `struct ngcomplex` is defined

If you try to **re-import** or **re-initialize**:

1. Ngspice tries to define `struct ngcomplex` again
2. C doesn't allow duplicate struct declarations
3. Error is thrown

### Why Filtering Works

By removing imports and using a **single shared namespace**:

- ✅ PySpice is imported **once** at module load time
- ✅ Each simulation uses the **same** Circuit() and unit objects
- ✅ No re-initialization occurs

---

**The fix is automatic - just run your circuit requests and the imports will be filtered!**
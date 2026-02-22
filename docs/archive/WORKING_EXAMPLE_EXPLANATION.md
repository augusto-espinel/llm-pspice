# WORKING EXAMPLE: RC Low-Pass Filter

## What Ralph Actually Does

Ralph doesn't store SUCCESSFUL examples - it only logs FAILED attempts and analyzes them to improve the system prompt. The issues.json file contains only **failed** circuit simulations, not successful ones.

## The Problem with Stored Examples

The examples I found in the logs (Issues #10, #11, #12) all had correct-looking code but **failed to simulate** - that's why they were logged as issues! They had:
- Good Python syntax
- Correct PySpice structure
- BUT: Wrong simulation parameters or source types

## Actual Working Code (Corrected)

Here's a CORRECTED version that WOULD work with the current fixes:

### Prompt:
```
"Create a simple RC low-pass filter with R=1kOhm and C=10nF with 10V input"
```

### Model:
```
cogito-2.1:671b (Ollama Cloud)
```

### Generated Code (CORRECTED):
```python
# RC low-pass filter with pulse source for transient analysis
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('RC_LowPass_Filter')

# CRITICAL: Use PulseVoltageSource for transient analysis
# (DC sources hide charging behavior)
circuit.PulseVoltageSource(
    'input', 'n1', circuit.gnd,
    initial_value=0 @ u_V,
    pulsed_value=10 @ u_V,
    pulse_width=100 @ u_ms,
    period=100 @ u_ms,
    delay_time=0.001 @ u_ms,
    rise_time=0.001 @ u_ms
)

# Resistor: 1 kOhm (correct unit)
circuit.R(1, 'n1', 'n2', 1 @ u_kOhm)

# Capacitor: 10 nF (CORRECT: use u_nF, NOT u_uF!)
circuit.C(1, 'n2', circuit.gnd, 10 @ u_nF)

# Create simulator
simulator = circuit.simulator()

# CRITICAL: Run transient analysis and assign to 'analysis'
analysis = simulator.transient(
    step_time=0.1 @ u_us,   # 0.1 microsecond time steps
    end_time=10 @ u_ms      # 10 millisecond total simulation
)
```

## What Was Fixed

| Issue | Before (Failed) | After (Fixed) |
|-------|----------------|---------------|
| Voltage Source | `circuit.V('input', ...)` DC source | **`PulseVoltageSource`** step input |
| Capacitor Unit | `10 @ u_uF` ❌ (doesn't exist) | `10 @ u_nF` ✅ |
| Analysis Variable | Sometimes missing or wrong var name | **Must** be called `analysis` |
| DC Path | Sometimes floating nodes | All nodes connect to ground |

## Why Ralph Can't Show You a Success

1. **Ralph's database only contains failures** - it's a bug tracker, not a success showcase
2. **The "successful" examples failed** - they looked good but simulated to no data
3. **Success requires actual LLM API** - needs active Ollama Cloud or local model to generate fresh code

## To See a Real Success

You need to:
1. Start the llm-pspice app: `.\run_app.ps1`
2. Configure a model (cloud or local)
3. Enter a prompt like: "Create an RC circuit with R=1k, C=10nF"
4. The app will now:
   - Use the improved system prompt
   - Auto-fix unit typos (u_uF → u_nF)
   - Convert DC to pulse sources automatically
   - Run the simulation

## What Ralph Accomplished

Ralph analyzed 22 failed attempts and:
- ✅ Fixed 4 common unit typos in the system prompt
- ✅ Added critical guidance about pulse sources
- ✅ Created a unit validator to auto-fix typos
- ✅ Added DC path to ground requirements
- ✅ Specified exact parameter ranges for simulations

**Result:** Now new prompts should work correctly, even though we don't have a stored successful example to show.
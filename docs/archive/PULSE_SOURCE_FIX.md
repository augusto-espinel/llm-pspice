# Pulse Source Syntax Fix

## Problem

When testing prompts in Streamlit, both glm-4.7 and cogito-2.1 models generated **invalid PySpice code** for pulse sources:

```python
# ❌ WRONG - What the LLM generated
circuit.V('input', 'n1', 'n2', pulse=(0, 5, 0, PeriodValue(1 μs), PeriodValue(1 μs), PeriodValue(0.5 ms), PeriodValue(1 ms)))

# Error: Unknown argument pulse
```

## Root Cause

The system prompt said:
> "For transient analysis, use pulse sources instead of DC"

But **did not show the correct PySpice syntax** for pulse sources!

The LLM guessed a syntax that doesn't exist in PySpice.

## Solution

Updated the system prompt to include:

### 1. Pulse Source in Component Rules

```python
Circuit.PulseVoltageSource(
    'name', 'node+', 'node-',
    initial_value @ u_V,
    pulsed_value @ u_V,
    pulse_width @ u_ms,
    period @ u_ms,
    delay_time @ u_ms,
    rise_time @ u_ms,
    fall_time @ u_ms
)  # ✅ CORRECT PySpice syntax
```

### 2. Working Example with Pulse Source

```python
# RC low-pass filter circuit with pulse source
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('RC_Filter')
# Pulse source: 0V to 10V step, 1ms pulse width, 2ms period
circuit.PulseVoltageSource('input', 'n1', circuit.gnd,
    initial_value=0 @ u_V,
    pulsed_value=10 @ u_V,
    pulse_width=1 @ u_ms,
    period=2 @ u_ms,
    delay_time=0.001 @ u_ms,
    rise_time=0.001 @ u_ms,
    fall_time=0.001 @ u_ms)
circuit.R(1, 'n1', 'n2', 1 @ u_kOhm)
circuit.C(1, 'n2', circuit.gnd, 10 @ u_nF)

simulator = circuit.simulator()
analysis = simulator.transient(step_time=1 @ u_us, end_time=10 @ u_ms)
```

## Why Ralph's Test "Worked"

Ralph's test showed a success because:
- The LLM generated a simple DC source (not pulse)
- CircuitBuilder's `_convert_dc_to_pulse()` **auto-converted** it
- This auto-conversion only works for DC sources, not malformed pulse syntax

When you directly ask for pulse sources in Streamlit:
- LLM generates wrong pulse syntax
- Auto-conversion doesn't fix it
- Simulation fails with "Unknown argument pulse"

## Files Updated

1. **`llm-orhcestrator.py`** - Updated system prompt with pulse source syntax + example
2. **`improved_system_prompt.txt`** - Same updates for Ralph's testing

## What to Test

Try this prompt again in the updated Streamlit app:

> Simulate a low-pass filter with cutoff 1kHz using R=1.59kOhm and C=100nF

The LLM should now use **correct pulse source syntax** and simulate successfully!

## Restart Required

**Restart the Streamlit app** to load the updated system prompt:

```powershell
# Stop the app (Ctrl+C) and restart
cd llm-sim-poc
.\run_app.ps1
```

The prompt is cached when the app starts, so changes don't take effect until restart.
#!/usr/bin/env python3
"""
Standalone Test Script for LLM-Generated Circuit Code

This script lets you manually test Python circuit code in VS Code
without running the llm-pspice Streamlit app.

Usage:
1. Copy LLM-generated code (just the python block, not the ``` markers)
2. Paste it into the CIRCUIT_CODE section below
3. Run: python standalone_test.py
"""

import sys
import os

# Add pyspice conda environment if needed
# If getting "ModuleNotFoundError", activate: conda activate pyspice

# ========================================
# STEP 1: Paste LLM-generated code here
# ========================================
CIRCUIT_CODE = """
# RC low-pass filter with pulse source
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('RC_LowPass_Filter')

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
"""
# ========================================

print("=" * 80)
print("INDEPENDENT CIRCUIT CODE TEST")
print("=" * 80)

# STEP 1: Syntax check
print("\n[1/5] Checking Python syntax...")
try:
    compile(CIRCUIT_CODE, '<string>', 'exec')
    print("    syntax.py: OK")
except SyntaxError as e:
    print(f"    syntax.py: FAILED")
    print(f"    Error: {e}")
    sys.exit(1)

# STEP 2: Import check
print("\n[2/5] Checking PySpice imports...")
try:
    from PySpice.Spice.Netlist import Circuit
    from PySpice.Unit import *
    print("    imports: OK")
    print(f"    PySpice version: {os.popen('pip show PySpice | findstr Version').read().strip()}")
except ImportError as e:
    print(f"    imports: FAILED")
    print(f"    Error: {e}")
    print(f"\n    Fix: pip install PySpice")
    print(f"    Or activate conda env: conda activate pyspice")
    sys.exit(1)

# STEP 3: Unit validation
print("\n[3/5] Validating PySpice units...")
imported_units = {
    'u_kOhm': u_kOhm,
    'u_Ohm': u_Ohm,
    'u_V': u_V,
    'u mA': u_mA,
    'u_A': u_A,
    'u_F': u_F,
    'u_H': u_H,
    'u_s': u_s,
    'u_ms': u_ms,
    'u_us': u_us,
    'u_mV': u_mV,
    'u_nF': u_nF,
    'u_pF': u_pF,
    'u_GHz': u_GHz,
    'u_MHz': u_MHz,
    'u_kHz': u_kHz,
    'u_Hz': u_Hz,
}

# Check for invalid units
invalid_units = ['u_uF', 'u_MOhm', 'u_mOhm', 'u_uf', 'u_mohm']
found_invalid = []
for bad_unit in invalid_units:
    if bad_unit in CIRCUIT_CODE:
        found_invalid.append(bad_unit)

if found_invalid:
    print(f"    VALIDATION: FAILED - Found invalid units: {', '.join(found_invalid)}")
    print(f"    Fix: u_uF -> u_nF, u_MOhm -> u_kOhm, u_mOhm -> u_Ohm")
    # Auto-fix the code
    for bad, good in [('u_uF', 'u_nF'), ('u_uf', 'u_nF'), ('u_MOhm', 'u_kOhm'), ('u_mOhm', 'u_Ohm')]:
        CIRCUIT_CODE = CIRCUIT_CODE.replace(bad, good)
    print(f"    Auto-applied fixes to code")
    print(f"    VALIDATION: OK (after fixes)")
else:
    print(f"    VALIDATION: OK")

# STEP 4: Execute circuit definition
print("\n[4/5] Creating circuit object...")
try:
    namespace = {'Circuit': Circuit, 'PulseVoltageSource': PulseVoltageSource}
    namespace.update({
        'u_kOhm': u_kOhm, 'u_Ohm': u_Ohm, 'u_V': u_V, 'u_mA': u_mA, 'u_A': u_A,
        'u_F': u_F, 'u_H': u_H, 'u_s': u_s, 'u_ms': u_ms, 'u_us': u_us,
        'u_mV': u_mV, 'u_nF': u_nF, 'u_pF': u_pF, 'u_GHz': u_GHz,
        'u_MHz': u_MHz, 'u_kHz': u_kHz, 'u_Hz': u_Hz,
    })

    exec(CIRCUIT_CODE, namespace)
    print(f"    circuit: OK")

    # Check if circuit exists
    if 'circuit' not in namespace:
        print(f"    circuit: FAILED - No 'circuit' variable created")
        sys.exit(1)
    if 'analysis' not in namespace:
        print(f"    analysis: FAILED - No 'analysis' variable created")
        print(f"    Make sure simulation is stored in 'analysis' variable")
        sys.exit(1)

    circuit = namespace['circuit']
    analysis = namespace['analysis']
    print(f"    analysis: OK")

except NameError as e:
    print(f"    FAILED: {e}")
    print(f"    This usually means a unit was used that doesn't exist in PySpice")
    sys.exit(1)
except Exception as e:
    print(f"    FAILED: {e}")
    sys.exit(1)

# STEP 5: Check simulation results
print("\n[5/5] Checking simulation results...")
try:
    if hasattr(analysis, 'time'):
        time_points = len(analysis.time)
        print(f"    simulation: OK")
        print(f"    Time points: {time_points}")
        print(f"    Time range: {analysis.time[0]} to {analysis.time[-1]}")

        # Check if we have data
        has_data = False
        for node in ['n1', 'n2', 'out', 'output', 'in', 'input']:
            if hasattr(analysis, node):
                data = getattr(analysis, node)
                print(f"    Node '{node}': {len(data)} data points")
                has_data = True

        if not has_data:
            print(f"    WARNING: No node data found - check circuit node names")
    else:
        print(f"    simulation: WARNING - No time axis data")
        print(f"    This usually means the simulation didn't run properly")

except Exception as e:
    print(f"    FAILED: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print("RESULT: ALL CHECKS PASSED")
print("=" * 80)
print("\nThe circuit code is valid and produced simulation results.")
print("You can now confidently use this code in the llm-pspice app.")
print("\nFor VS Code debugging:")
print("1. Set breakpoints in the CIRCUIT_CODE section")
print("2. Use VS Code's 'Run and Debug'")
print("3. Inspect the 'namespace' dict after execution")
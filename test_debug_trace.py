#!/usr/bin/env python3
"""
Test with full debug tracing to see what code gets executed
"""

import sys
sys.path.insert(0, '.')

from circuit_builder import CircuitBuilder

# Circuit code - same as before
circuit_code = """# RC low-pass filter with cutoff 1kHz
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('LowPassFilter_1kHz')

# Input voltage source (pulse to see transient response)
circuit.PulseVoltageSource('input', 'input_node', circuit.gnd,
    initial_value=0 @ u_V,
    pulsed_value=5 @ u_V,
    pulse_width=5 @ u_ms,
    period=10 @ u_ms,
    delay_time=0.001 @ u_ms,
    rise_time=0.001 @ u_ms,
    fall_time=0.001 @ u_ms)

# RC filter: R=1.59kOhm, C=100nF → fc≈1kHz
circuit.R(1, 'input_node', 'output_node', 1.59 @ u_kOhm)
circuit.C(1, 'output_node', circuit.gnd, 100 @ u_nF)

# Run transient simulation
simulator = circuit.simulator()
analysis = simulator.transient(step_time=10 @ u_us, end_time=10 @ u_ms)
"""

print("=" * 70)
print("ORIGINAL CODE:")
print("=" * 70)
print(circuit_code)
print()

# Manually run the filtering steps to see what happens
from error_handler import validate_circuit_code
from unit_validator import fix_pyspice_units
import re

filtered_code = circuit_code

# Step 1: Filter imports
import_filter_pattern = r'^from PySpice\.|^import PySpice'
filtered_code = '\n'.join([line for line in filtered_code.split('\n')
                         if not re.match(import_filter_pattern, line)])

print("=" * 70)
print("AFTER FILTERING IMPORTS:")
print("=" * 70)
print(filtered_code)
print()

# Step 2: Fix units
filtered_code = fix_pyspice_units(filtered_code)

print("=" * 70)
print("AFTER FIXING UNITS:")
print("=" * 70)
print(filtered_code)
print()

# Step 3: Check if code is valid
is_valid, validation_error = validate_circuit_code(filtered_code)
print(f"Validation: {'PASS' if is_valid else 'FAIL'}")
if validation_error:
    print(f"Error: {validation_error}")
print()

# Now try to simulate directly
print("=" * 70)
print("TESTING DIRECT SIMULATION:")
print("=" * 70)

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
import numpy as np

try:
    # Create circuit directly (not using filtered code)
    circuit2 = Circuit('DirectTest')
    circuit2.PulseVoltageSource('input', 'input_node', circuit2.gnd,
        initial_value=0 @ u_V,
        pulsed_value=5 @ u_V,
        pulse_width=5 @ u_ms,
        period=10 @ u_ms,
        delay_time=0.001 @ u_ms,
        rise_time=0.001 @ u_ms,
        fall_time=0.001 @ u_ms)

    circuit2.R(1, 'input_node', 'output_node', 1.59 @ u_kOhm)
    circuit2.C(1, 'output_node', circuit2.gnd, 100 @ u_nF)

    simulator = circuit2.simulator()
    analysis = simulator.transient(step_time=10 @ u_us, end_time=10 @ u_ms)

    input_voltage = analysis['input_node']
    input_values = np.array(input_voltage.values) if hasattr(input_voltage, 'values') else np.array(input_voltage)
    max_input = np.max(input_values)

    print(f"✓ Direct simulation works!")
    print(f"  Max input voltage: {max_input}V")
    print(f"  Time points: {len(analysis.time)}")

    if max_input < 0.1:
        print("  ⚠ WARNING: Input voltage is near zero!")

except Exception as e:
    print(f"✗ Direct simulation failed: {e}")
    import traceback
    traceback.print_exc()
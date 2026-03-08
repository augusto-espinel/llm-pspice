#!/usr/bin/env python3
"""
Test low-pass filter simulation with pre-written code
"""

import sys
sys.path.insert(0, '.')

from circuit_builder import CircuitBuilder

# Generate a valid low-pass filter code (simple RC, cutoff ~1kHz)
# fc = 1 / (2*pi*R*C)
# For 1kHz: R*C = 1/(2*pi*1000) ≈ 159 microseconds
# Use R=1.59kOhm, C=100nF → R*C = 159 us → fc ≈ 1kHz

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

print("Testing low-pass filter simulation with pre-written code...")
print("=" * 70)
print("Circuit: RC low-pass filter, R=1.59kΩ, C=100nF, fc≈1kHz")
print()

try:
    builder = CircuitBuilder()
    print("Running simulation...")

    result = builder.run_simulation(circuit_code)

    print(f"\n✓ Simulation successful!")
    print(f"  Data points: {len(result.get('data', []))}")
    print(f"  Variables: {result.get('variables', [])[:5]}")  # Show first 5
    print(f"  Success: {result.get('success', False)}")

except Exception as e:
    print(f"\n✗ Simulation failed!")
    import traceback
    traceback.print_exc()
    print(f"\nError: {e}")
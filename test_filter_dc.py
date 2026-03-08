#!/usr/bin/env python3
"""
Test low-pass filter simulation with DC source (no pulse)
"""

import sys
sys.path.insert(0, '.')

from circuit_builder import CircuitBuilder
from PySpice.Unit import *

# Test with simple DC source
circuit_code = """# RC low-pass filter with DC source
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('LowPassFilter_DC')

# Simple DC voltage source
circuit.V('input', 'input_node', circuit.gnd, 5 @ u_V)

# RC filter: R=1.59kOhm, C=100nF → fc≈1kHz
circuit.R(1, 'input_node', 'output_node', 1.59 @ u_kOhm)
circuit.C(1, 'output_node', circuit.gnd, 100 @ u_nF)

# Run transient simulation
simulator = circuit.simulator()
analysis = simulator.transient(step_time=10 @ u_us, end_time=10 @ u_ms)
"""

print("Testing low-pass filter with DC source...")
print("=" * 70)

try:
    builder = CircuitBuilder()
    # Manually disable pulse conversion by setting the attribute
    builder.use_pulse_sources = False
    print("Running simulation (DC source, pulse conversion disabled)...\n")

    result = builder.run_simulation(circuit_code)

    if result.get('error'):
        print(f"✗ Simulation failed!")
        print(f"Error: {result['error']}")
    else:
        print(f"✓ Simulation completed!")
        print(f"  Data points: {len(result.get('data', []))}")
        print(f"  Plots generated: {len(result.get('plots', []))}")

        # Show sample data
        if result.get('data'):
            print(f"\n  Sample data (first 5 points):")
            for i, point in enumerate(result['data'][:5]):
                time_ms = point['time'] * 1000
                var = point['variable']
                val = point['value']
                print(f"    t={time_ms:6.2f}ms, {var:12s} = {val:.6f}V")

except Exception as e:
    print(f"✗ Test failed with exception!")
    import traceback
    traceback.print_exc()
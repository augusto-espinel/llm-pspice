#!/usr/bin/env python3
"""
Test pulse source generation manually to see netlist
"""

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('PulseTest')

# Generate a pulse source
circuit.PulseVoltageSource('input', 'n1', circuit.gnd,
    initial_value=0 @ u_V,
    pulsed_value=5 @ u_V,
    pulse_width=5 @ u_ms,
    period=10 @ u_ms,
    delay_time=0.001 @ u_ms,
    rise_time=0.001 @ u_ms,
    fall_time=0.001 @ u_ms)

# Add a load resistor
circuit.R(1, 'n1', circuit.gnd, 1 @ u_kOhm)

# Print the circuit string
print("Generated SPICE netlist:")
print("=" * 70)
print(str(circuit))

# Now try to simulate
print("\nRunning simulation...")
try:
    simulator = circuit.simulator()
    analysis = simulator.transient(step_time=10 @ u_us, end_time=10 @ u_ms)

    print(f"Simulation successful!")
    print(f"Time points: {len(analysis.time)}")

    # Check n1 voltage
    n1_voltage = analysis['n1']
    print(f"n1 voltage: {n1_voltage}")

    # Check if values are non-zero
    import numpy as np
    n1_values = np.array(n1_voltage.values) if hasattr(n1_voltage, 'values') else np.array(n1_voltage)
    max_val = np.max(n1_values)
    print(f"Max n1 voltage: {max_val}V")

    if max_val < 0.1:
        print("⚠ WARNING: n1 voltage is near zero - pulse not working!")
    else:
        print("✓ n1 voltage looks good")

except Exception as e:
    print(f"Simulation failed: {e}")
    import traceback
    traceback.print_exc()
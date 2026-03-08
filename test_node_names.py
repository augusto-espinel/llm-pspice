#!/usr/bin/env python3
"""
Test different node names to see if 'input_node' causes issues
"""

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
import numpy as np

def test_node_name(node_name_plus, node_name_minus, description):
    print(f"\n{'='*70}")
    print(f"Testing: {description}")
    print(f"Node names: '{node_name_plus}', '{node_name_minus}'")
    print('='*70)

    circuit = Circuit('NodeTest')

    # Create pulse source with given node names
    circuit.PulseVoltageSource('input', node_name_plus, node_name_minus,
        initial_value=0 @ u_V,
        pulsed_value=5 @ u_V,
        pulse_width=5 @ u_ms,
        period=10 @ u_ms,
        delay_time=0.001 @ u_ms,
        rise_time=0.001 @ u_ms,
        fall_time=0.001 @ u_ms)

    # Add load resistor
    circuit.R(1, node_name_plus, node_name_minus, 1 @ u_kOhm)

    try:
        simulator = circuit.simulator()
        analysis = simulator.transient(step_time=10 @ u_us, end_time=10 @ u_ms)

        # Check voltage
        voltage = analysis[str(node_name_plus)]
        voltage_values = np.array(voltage.values) if hasattr(voltage, 'values') else np.array(voltage)
        max_val = np.max(voltage_values)

        print(f"  Max voltage: {max_val}V")
        if max_val > 0.1:
            print(f"  ✓ SUCCESS")
            return True
        else:
            print(f"  ✗ FAILED - voltage is zero")
            return False

    except Exception as e:
        print(f"  ✗ EXCEPTION: {e}")
        return False

# Test various node names
results = []

# Get a circuit instance for gnd reference
circuit_ref = Circuit('Temp')
gnd_ref = circuit_ref.gnd

results.append(('input_node + gnd_ref', test_node_name('input_node', gnd_ref, "'input_node' + circuit.gnd")))
results.append(('input_node + quoted gnd', test_node_name('input_node', '0', "'input_node' + '0'")))
results.append(('n1 + gnd_ref', test_node_name('n1', gnd_ref, "'n1' + circuit.gnd (benchmark)")))
results.append(('n1 + 0', test_node_name('n1', '0', "'n1' + '0' (baseline)")))

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
for desc, success in results:
    status = "✓" if success else "✗"
    print(f"{status} {desc}")
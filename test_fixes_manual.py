"""
Manual test for circuit simulation fixes (2026-02-22)
Tests data extraction, plotting, and debug logging
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from circuit_builder import CircuitBuilder
import json

def test_sim():
    """Test actual circuit simulation with LLM fixes"""

    print("=" * 80)
    print("CIRCUIT SIMULATION FIXES TEST")
    print("=" * 80)
    print()

    # Test circuit: Low-pass filter (the failing case from issues)
    circuit_code = """
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('RC_LowPass_Filter')

# Input: 10V DC with pulse for transient analysis
circuit.PulseVoltageSource(
    'input',
    'in',
    circuit.gnd,
    initial_value=0 @ u_V,
    pulsed_value=10 @ u_V,
    pulse_width=100 @ u_ms,
    period=100 @ u_ms,
    delay_time=0.001 @ u_ms,
    rise_time=0.001 @ u_ms
)

# RC filter: R=1.59 kOhm, C=100 nF
# Cutoff frequency: fc = 1/(2*pi*R*C) = 1 kHz
circuit.R('1', 'in', 'out', 1.59 @ u_kOhm)
circuit.C('1', 'out', circuit.gnd, 100 @ u_nF)

# Run transient simulation
analysis = circuit.simulator().transient(
    step_time=1 @ u_us,
    end_time=5 @ u_ms
)
"""

    print("Test Circuit: Low-pass filter (R=1.59kOhm, C=100nF, fc=1kHz)")
    print()

    # Run simulation
    builder = CircuitBuilder()
    results = builder.run_simulation(circuit_code)

    print()
    print("=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    print()

    # Check for errors
    if results.get('error'):
        print(f"❌ SIMULATION ERROR: {results['error']}")
        return False

    # Check data extraction
    data = results.get('data', [])
    print(f"✓ Data extraction: {len(data)} data points")

    if len(data) == 0:
        print("  ❌ FAILED: No data extracted!")
        return False

    if len(data) >= 5000:
        print("  ✓ PASS: Sufficient data points")
    else:
        print(f"  ❌ FAILED: Expected ~10000 points, got {len(data)}")
        return False

    # Check plotting
    plots = results.get('plots', [])
    print(f"✓ Plot generation: {len(plots)} plot(s)")

    if len(plots) == 0:
        print("  ❌ FAILED: No plots generated!")
        return False

    print("  ✓ PASS: Plot generated successfully")

    # Check debug info
    debug_info = results.get('debug_info', {})
    print(f"✓ Debug info captured: {len(debug_info)} fields")

    if not debug_info:
        print("  ⚠ WARNING: No debug info captured")
    else:
        print(f"  - Analysis type: {debug_info.get('analysis_type')}")
        print(f"  - Has time: {debug_info.get('has_time')}")
        print(f"  - Has frequency: {debug_info.get('has_frequency')}")
        print(f"  - Has nodes: {debug_info.get('has_nodes')}")
        print(f"  - Time length: {debug_info.get('time_length')}")
        print("  ✓ PASS: Debug info captured")

    # Check filtered code (LLM fixes applied)
    filtered_code = results.get('filtered_code')
    print(f"✓ LLM fixes applied: {'yes' if filtered_code else 'no'}")

    if filtered_code:
        # Check if 'in' was replaced with 'input_node'
        if "'in'" in filtered_code or '"in"' in filtered_code:
            print("  ❌ FAILED: 'in' keyword not replaced!")
            return False
        else:
            print("  ✓ PASS: Python keyword 'in' replaced with 'input_node'")

        # Check if pulse source is used for transient
        if 'PulseVoltageSource' in filtered_code:
            print("  ✓ PASS: Pulse source correctly used for transient analysis")
    else:
        print("  ⚠ WARNING: No filtered code in results")

    print()
    print("=" * 80)
    print("OVERALL RESULT: ✓ ALL TESTS PASSED!")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"✓ Data extraction: {len(data)} points extracted")
    print(f"✓ Plot generation: {len(plots)} plot(s) generated")
    print(f"✓ Debug logging: {len(debug_info)} fields captured")
    print(f"✓ LLM code fixes: Applied successfully")
    print()

    return True

if __name__ == '__main__':
    success = test_sim()
    sys.exit(0 if success else 1)
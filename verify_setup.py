#!/usr/bin/env python3
"""
Quick test to verify your PySpice setup works

This uses a known-good circuit example.
"""

print("Testing PySpice Setup...")
print("=" * 60)

try:
    # Test 1: Import PySpice
    print("\n[1] Testing PySpice imports...")
    from PySpice.Spice.Netlist import Circuit
    from PySpice.Unit import *
    print("    PySpice imports: OK")

    # Test 2: Build a simple circuit
    print("\n[2] Building test circuit...")
    circuit = Circuit('Test_RC')
    circuit.PulseVoltageSource(
        'input', 'n1', circuit.gnd,
        initial_value=0 @ u_V,
        pulsed_value=5 @ u_V,
        pulse_width=50 @ u_ms,
        period=100 @ u_ms,
        delay_time=0.001 @ u_ms,
        rise_time=0.001 @ u_ms
    )
    circuit.R(1, 'n1', 'n2', 1 @ u_kOhm)
    circuit.C(1, 'n2', circuit.gnd, 10 @ u_nF)
    print("    Circuit created: OK")

    # Test 3: Run simulation
    print("\n[3] Running simulation...")
    simulator = circuit.simulator()
    analysis = simulator.transient(step_time=0.1 @ u_us, end_time=5 @ u_ms)
    print("    Simulation: OK")

    # Test 4: Check results
    print("\n[4] Checking results...")
    time_points = len(analysis.time)
    if time_points > 0:
        print(f"    Time points: {time_points}")
        print(f"    Time range: {analysis.time[0]:.6f} to {analysis.time[-1]:.6f} s")
        print(f"    Results: OK")
    else:
        print("    ERROR: No time points generated!")
        exit(1)

    print("\n" + "=" * 60)
    print("SUCCESS: PySpice setup is working correctly!")
    print("=" * 60)
    print("\nYou can now use standalone_test.py to verify LLM-generated code.")
    print("\nNext steps:")
    print("1. Run: python standalone_test.py")
    print("2. Paste LLM code into CIRCUIT_CODE section")
    print("3. Run again to validate")

except ImportError as e:
    print(f"\nERROR: {e}")
    print("\nPySpice not installed or conda environment not activated.")
    print("\nFix with:")
    print("  conda activate pyspice")
    print("  pip install PySpice")

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
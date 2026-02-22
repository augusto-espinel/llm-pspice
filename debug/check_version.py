"""
Check simulator attributes and run simple test
"""

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
import numpy as np

print("="*60)
print("RC Circuit Test - Check ngspice version")
print("="*60)
print()

# Circuit parameters
R = 1000  # 1 kOhm
C = 10e-6  # 10 uF
V_in = 10  # 10 Volts
tau = R * C

print(f"Circuit: R={R} Ohms, C={C*1e6:.1f} uF, Vin={V_in} V")
print()

# Create circuit
circuit = Circuit('SimpleRC')
circuit.V('input', 'n1', circuit.gnd, V_in @ u_V)
circuit.R(1, 'n1', 'n2', R @ u_Ohm)
circuit.C(1, 'n2', circuit.gnd, C @ u_F)

print("Running simulation...")
try:
    simulator = circuit.simulator()

    # Check what attributes are available
    print("\nSimulator attributes:")
    for attr in dir(simulator):
        if not attr.startswith('_'):
            print(f"  - {attr}")

    print("\nRunning transient analysis...")

    analysis = simulator.transient(
        step_time=(tau/100) @ u_s,
        end_time=(5*tau) @ u_s
    )

    time_array = np.array(analysis.time) * 1000
    voltage_cap = np.array(analysis['n2'])

    print(f"\nSimulation completed!")
    print(f"  Data points: {len(time_array)}")
    print(f"  Final capacitor voltage: {voltage_cap[-1]:.4f} V")
    print(f"  Expected: {V_in * (1 - np.exp(-5)):.4f} V")
    print()

    # Check initial and final values
    print(f"  Initial V_cap: {voltage_cap[0]:.4f} V")
    print(f"  Final V_cap: {voltage_cap[-1]:.4f} V")

    expected_final = V_in * (1 - np.exp(-5))
    error = abs(voltage_cap[-1] - expected_final)
    error_pct = (error / expected_final * 100) if expected_final > 0 else 0

    print(f"  Absolute error: {error:.4f} V")
    print(f"  Relative error: {error_pct:.2f}%")

    if error_pct < 5:
        print("\n[SUCCESS] Simulation is accurate!")
    else:
        print("\n[ISSUE] Simulation is NOT accurate")

except Exception as e:
    print(f"\n[FAIL] {e}")
    import traceback
    traceback.print_exc()

print()
print("="*60)
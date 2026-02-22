"""Quick test to check if circuit simulation actually works"""
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
import numpy as np

# Create a simple RC circuit
circuit = Circuit('RC_Test')
circuit.PulseVoltageSource(
    'input', 'n1', circuit.gnd,
    initial_value=0 @ u_V,
    pulsed_value=5 @ u_V,
    pulse_width=10 @ u_ms,
    period=20 @ u_ms,
    delay_time=0.1 @ u_ms,
    rise_time=0.1 @ u_ms
)
circuit.R(1, 'n1', 'n2', 1 @ u_kOhm)
circuit.C(1, 'n2', circuit.gnd, 10 @ u_uF)

print("Creating simulator...")
simulator = circuit.simulator()

print("Running transient analysis...")
analysis = simulator.transient(step_time=1 @ u_us, end_time=5 @ u_ms)

print(f"Time points: {len(analysis.time)}")
print(f"Time range: {analysis.time[0]} to {analysis.time[-1]} s")

# Check voltage data
try:
    v1 = analysis['n1']
    v1_np = np.array(v1.as_ndarray())
    print(f"Input n1: min={v1_np.min():.3f}V, max={v1_np.max():.3f}V, mean={v1_np.mean():.3f}V")
except (IndexError, KeyError):
    print("ERROR: Node 'n1' not found in analysis")

try:
    v2 = analysis['n2']
    v2_np = np.array(v2.as_ndarray())
    print(f"Output n2: min={v2_np.min():.3f}V, max={v2_np.max():.3f}V, mean={v2_np.mean():.3f}V")
except (IndexError, KeyError):
    print("ERROR: Node 'n2' not found in analysis")

# Check if data is valid
try:
    v1_max = max(analysis['n1'].as_ndarray())
    if v1_max > 1:
        print("\n✅ SUCCESS: Simulation works, data is valid!")
    else:
        print("\n❌ FAIL: All data is near zero - ngspice version issue!")
except (IndexError, KeyError):
    print("\n❌ Cannot validate data - node access failed")
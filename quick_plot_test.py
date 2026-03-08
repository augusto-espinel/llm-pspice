"""Quick test to generate and save a plot from circuit simulation"""
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
import numpy as np
import matplotlib.pyplot as plt

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

# Extract data
time = analysis.time.as_ndarray()
v1 = analysis['n1'].as_ndarray()
v2 = analysis['n2'].as_ndarray()

print(f"Input n1: min={v1.min():.3f}V, max={v1.max():.3f}V, mean={v1.mean():.3f}V")
print(f"Output n2: min={v2.min():.3f}V, max={v2.max():.3f}V, mean={v2.mean():.3f}V")

# Generate plot
plt.figure(figsize=(10, 6))
plt.plot(time * 1000, v1, label='Input (n1)', linewidth=2)
plt.plot(time * 1000, v2, label='Output (n2)', linewidth=2)
plt.xlabel('Time (ms)', fontsize=12)
plt.ylabel('Voltage (V)', fontsize=12)
plt.title('RC Circuit Simulation - Pulse Response', fontsize=14, fontweight='bold')
plt.legend(loc='best', fontsize=10)
plt.grid(True, alpha=0.3)
plt.tight_layout()

# Save the plot
plot_filename = 'last_simulation_plot.png'
plt.savefig(plot_filename, dpi=150, bbox_inches='tight')
plt.close()

print(f"\n✅ Plot saved to: {plot_filename}")
print(f"File location: C:\\Users\\augus\\.openclaw\\workspace\\llm-sim-poc\\{plot_filename}")
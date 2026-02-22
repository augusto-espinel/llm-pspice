from PySpice.Spice.Netlist import Circuit
import PySpice

print(f'PySpice version: {PySpice.__version__}')

# Create a simple test circuit
circuit = Circuit('Test')
circuit.V('input', 'n1', circuit.gnd, 5)
circuit.R(1, 'n1', 'n2', 1e3)
circuit.C(1, 'n2', circuit.gnd, 1e-6)

try:
    simulator = circuit.simulator()
    print('ngspice initialized successfully!')
    print('ngspice version should now be 38')
except Exception as e:
    print(f'Error: {e}')
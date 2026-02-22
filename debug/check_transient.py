"""
Check what arguments are accepted by transient()
"""

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('Test')
circuit.V('input', 'n1', circuit.gnd, 10 @ u_V)
circuit.R(1, 'n1', 'n2', 1000 @ u_Ohm)
circuit.C(1, 'n2', circuit.gnd, 10e-6 @ u_F)

import inspect
simulator = circuit.simulator()

print("Transient method signature:")
print(inspect.signature(simulator.transient))
print()
print("Transient method docstring:")
print(simulator.transient.__doc__)
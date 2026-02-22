"""
Find the correct import for pulse source
"""

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
import inspect

# Check what's in PySpice.Probe.WaveForm
try:
    from PySpice import Probe
    print("Available in PySpice.Probe:")
    print(dir(Probe))
    print()

    from PySpice.Probe import WaveForm
    print("Available in WaveForm:")
    print([x for x in dir(WaveForm) if 'Pulse' in x or 'Voltage' in x])
    print()

except Exception as e:
    print(f"Error: {e}")

# Check Circuit method for creating sources
circuit = Circuit('Test')
print("Circuit.V signature:")
print(inspect.signature(circuit.V))
print()

# Try to find pulse source in the library
import PySpice
print("PySpice attributes:")
for attr in dir(PySpice):
    if not attr.startswith('_') and 'Pulse' in attr:
        print(f"  {attr}")
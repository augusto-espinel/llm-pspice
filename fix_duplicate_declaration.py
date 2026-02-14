"""
Fix for Ngspice duplicate declaration error
Diagnoses and fixes the duplicate struct ngcomplex error
"""

import sys
import traceback

# Test code that would cause this error
problem_code = """
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

# First circuit definition
circuit = Circuit('Test1')
circuit.V('input', 'n1', circuit.gnd, 1 @ u_V)
circuit.R(1, 'n1', circuit.gnd, 1 @ u_kOhm)

# Second circuit definition (this causes the error if exec'd in same namespace)
circuit = Circuit('Test2')
circuit.V('input', 'n1', circuit.gnd, 5 @ u_V)
circuit.R(1, 'n1', circuit.gnd, 2 @ u_kOhm)

simulator = circuit.simulator()
analysis = simulator.transient(step_time=0.1 @ u_ms, end_time=1 @ u_ms)
"""

print("=" * 70)
print("Diagnosing Duplicate Declaration Error")
print("=" * 70)

# Test 1: Check if the issue is with multiple exec calls
print("\n[TEST 1] Executing code once - should work")
try:
    from PySpice.Spice.Netlist import Circuit
    from PySpice.Unit import *

    namespace = {
        'Circuit': Circuit,
        'u_kOhm': u_kOhm,
        'u_Ohm': u_Ohm,
        'u_V': u_V,
        'u_mA': u_mA,
        'u_A': u_A,
        'u_F': u_F,
        'u_s': u_s,
        'u_ms': u_ms,
    }

    # Clean code without duplicates
    clean_code = """
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('Test')
circuit.V('input', 'n1', circuit.gnd, 1 @ u_V)
circuit.R(1, 'n1', circuit.gnd, 1 @ u_kOhm)

simulator = circuit.simulator()
analysis = simulator.transient(step_time=0.1 @ u_ms, end_time=1 @ u_ms)
"""

    exec(compile(clean_code, '<string>', 'exec'), namespace)
    print("✅ Single execution works fine")

    circuit = namespace.get('circuit')
    print(f"Circuit created: {circuit}")

except Exception as e:
    print(f"❌ Error: {e}")
    traceback.print_exc()

# Test 2: Check if the issue is with duplicate imports in code
print("\n[TEST 2] Code with duplicate imports - should still work")
try:
    from PySpice.Spice.Netlist import Circuit
    from PySpice.Unit import *

    namespace = {
        'Circuit': Circuit,
        'u_kOhm': u_kOhm,
        'u_Ohm': u_Ohm,
        'u_V': u_V,
    }

    # Code with imports in it (LLM generated code often has this)
    code_with_imports = """
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('Test')
circuit.V('input', 'n1', circuit.gnd, 1 @ u_V)
circuit.R(1, 'n1', circuit.gnd', 2 @ u_kOhm)
"""

    exec(compile(code_with_imports, '<string>', 'exec'), namespace)
    print("✅ Code with imports works")

except Exception as e:
    print(f"❌ Error (this is the issue!): {e}")

print("\n" + "=" * 70)
print("SOLUTION")
print("=" * 70)
print("""
The duplicate declaration error is caused by PySpice being initialized
multiple times in the same Python process.

FIX: Create a fresh namespace for each execution OR filter out imports
""")
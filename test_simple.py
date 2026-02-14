"""
Simple test to verify installation
"""

import sys

print("=" * 60)
print("Testing Package Installation")
print("=" * 60)

# Test 1: Imports
print("\nTesting imports...")
packages = {
    "PySpice": "PySpice",
    "streamlit": "streamlit",
    "pandas": "pandas",
    "matplotlib": "matplotlib",
    "numpy": "numpy"
}

all_installed = True
for name, module in packages.items():
    try:
        __import__(module)
        print(f"  [OK] {name}")
    except ImportError as e:
        print(f"  [FAIL] {name}")
        all_installed = False

if all_installed:
    print("\n[SUCCESS] All packages installed!")
else:
    print("\n[ERROR] Some packages missing")
    sys.exit(1)

# Test 2: PySpice import
print("\nTesting PySpice components...")
try:
    from PySpice.Spice.Netlist import Circuit
    from PySpice.Unit import u_Ohm, u_V, u_kOhm, u_F, u_ms, u_us
    print("  [OK] PySpice imports")
except ImportError as e:
    print(f"  [FAIL] PySpice: {e}")
    sys.exit(1)

# Test 3: Try to create a circuit (without running simulation - needs ngspice)
print("\nTesting circuit creation...")
try:
    circuit = Circuit('Test_Circuit')
    circuit.V('input', 'n1', circuit.gnd, 10 @ u_V)
    circuit.R(1, 'n1', circuit.gnd, 1 @ u_kOhm)
    print("  [OK] Circuit created successfully")
except Exception as e:
    print(f"  [FAIL] Circuit creation: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("[SUCCESS] Basic installation verified!")
print("=" * 60)
print("\nNOTE: Full simulation test requires ngspice to be installed")
print("Download from: https://ngspice.sourceforge.io/downloads.html")
print("\nAfter installing ngspice, run: streamlit run app.py")
print("=" * 60)
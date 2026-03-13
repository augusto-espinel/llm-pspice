"""
Debug script: test diode bridge rectifier in PySpice
Run with: C:\Users\augus\anaconda3\envs\pyspice\python.exe debug_diode.py
"""
import sys
print("Python:", sys.version)

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
from PySpice.Spice.HighLevelElement import SinusoidalVoltageSource

# ── Test 1: Does circuit.D() work without a model? ──────────────────────────
print("\n--- Test 1: circuit.D() without model ---")
try:
    c = Circuit('DiodeNoModel')
    c.SinusoidalVoltageSource('input', 'ac_pos', c.gnd, amplitude=10@u_V, frequency=50@u_Hz)
    c.D(1, 'ac_pos', 'dc_out')   # no model → default
    c.R('load', 'dc_out', c.gnd, 1@u_kOhm)
    sim = c.simulator()
    analysis = sim.transient(step_time=0.1@u_ms, end_time=40@u_ms)
    print("  OK - time points:", len(analysis.time))
except Exception as e:
    print("  FAIL:", type(e).__name__, str(e)[:200])

# ── Test 2: circuit.D() WITH an explicit model ────────────────────────────
print("\n--- Test 2: circuit.D() with model ---")
try:
    c2 = Circuit('DiodeWithModel')
    c2.SinusoidalVoltageSource('input', 'ac_pos', c2.gnd, amplitude=10@u_V, frequency=50@u_Hz)
    c2.model('D1N4148', 'D', Is=2.52e-9, Rs=0.568, N=1.752, Cjo=4e-12, M=0.4, tt=20e-9)
    c2.D(1, 'ac_pos', 'dc_out', model='D1N4148')
    c2.R('load', 'dc_out', c2.gnd, 1@u_kOhm)
    sim2 = c2.simulator()
    analysis2 = sim2.transient(step_time=0.1@u_ms, end_time=40@u_ms)
    print("  OK - time points:", len(analysis2.time))
except Exception as e:
    print("  FAIL:", type(e).__name__, str(e)[:200])

# ── Test 3: Full bridge rectifier with model (the real use case) ──────────
print("\n--- Test 3: Full diode bridge rectifier ---")
try:
    c3 = Circuit('BridgeRectifier')
    c3.SinusoidalVoltageSource('input', 'ac_pos', 'ac_neg', amplitude=10@u_V, frequency=50@u_Hz)
    c3.model('D1N4148', 'D', Is=2.52e-9, Rs=0.568, N=1.752, Cjo=4e-12, M=0.4, tt=20e-9)
    # Standard bridge: D1,D3 = positive half; D2,D4 = negative half
    c3.D(1, 'ac_pos', 'dc_pos', model='D1N4148')   # top-left
    c3.D(2, 'ac_neg', 'dc_pos', model='D1N4148')   # top-right
    c3.D(3, 'dc_neg', 'ac_pos', model='D1N4148')   # bottom-left
    c3.D(4, 'dc_neg', 'ac_neg', model='D1N4148')   # bottom-right
    c3.R('load', 'dc_pos', 'dc_neg', 1@u_kOhm)
    c3.V('gnd_ref', 'dc_neg', c3.gnd, 0@u_V)       # tie dc_neg to ground
    sim3 = c3.simulator()
    analysis3 = sim3.transient(step_time=0.1@u_ms, end_time=40@u_ms)
    print("  OK - time points:", len(analysis3.time))
except Exception as e:
    print("  FAIL:", type(e).__name__, str(e)[:200])

# ── Test 4: What the LLM generated (the failing code) ─────────────────────
print("\n--- Test 4: LLM-generated diode bridge (bad code from GPT-3.5) ---")
try:
    c4 = Circuit('Diode_Bridge_Rectifier')
    c4.V(1, 'in', c4.gnd, 10@u_V)
    c4.R(1, 'in', '1', 1@u_kOhm)
    c4.D(1, '1', '2')       # <- no model: will ngspice accept this?
    c4.D(2, '2', 'out')
    c4.D(3, 'out', '4')
    c4.D(4, '4', c4.gnd)
    c4.R(2, '2', '3', 1@u_kOhm)
    sim4 = c4.simulator()
    analysis4 = sim4.transient(step_time=1@u_us, end_time=10@u_ms)
    print("  OK - time points:", len(analysis4.time))
except Exception as e:
    print("  FAIL:", type(e).__name__, str(e)[:300])

print("\nDone.")

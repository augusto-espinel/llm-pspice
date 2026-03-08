"""
Test script to verify Monaco editor session state sync
Run with: streamlit run test_monaco_sync.py
"""

import streamlit as st
from streamlit_monaco import st_monaco

# Initialize session state
if 'editor_code' not in st.session_state:
    st.session_state.editor_code = ""

st.title("Monaco Session State Test")

st.markdown("### Set Initial Code")
test_code = """from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

# Create circuit
circuit = Circuit('RC_LowPass_Filter')

# Add components
circuit.PulseVoltageSource('input', 'in', circuit.gnd,
                          initial_value=0 @ u_V,
                          pulsed_value=10 @ u_V,
                          pulse_width=2 @ u_ms,
                          period=20 @ u_ms,
                          delay_time=1 @ u_ms,
                          rise_time=0.5 @ u_ms,
                          fall_time=0.5 @ u_ms)

circuit.R(1, 'in', 'out', 10 @ u_kOhm)
circuit.C(1, 'out', circuit.gnd, 1 @ u_nF)

# Simulate
simulator = circuit.simulator()
analysis = simulator.transient(step_time=10 @ u_ns, end_time=5 @ u_us)
"""

if st.button("Set Test Code in Session State"):
    st.session_state.editor_code = test_code
    st.success("✅ Set editor_code in session state")
    st.rerun()

st.markdown("### Session State Status")
if st.session_state.editor_code:
    st.success(f"✅ editor_code exists ({len(st.session_state.editor_code)} chars)")
else:
    st.warning("⚠️ editor_code is empty")

st.markdown("### Monaco Editor")
editor_code = st_monaco(
    value=st.session_state.editor_code,
    language="python",
    height="500px",
    lineNumbers=True
)

# Update session state when editor changes
if editor_code != st.session_state.editor_code:
    st.session_state.editor_code = editor_code
    st.info("🔄 Editor content updated")

st.markdown("### Current Session State")
st.code(st.session_state.editor_code, language='python')
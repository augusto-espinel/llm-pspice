"""
LLM-Powered Circuit Simulation Environment
Proof of Concept - Streamlit UI

IMPORTANT: Run this app using the conda environment with PySpice:
    activate conda environment: conda activate pyspice
    then: streamlit run app.py

The pyspice conda environment (Python 3.10, PySpice 1.5, ngspice 38) is
required for accurate circuit simulations.

DATA STORAGE: All simulation data is stored OUTSIDE the workspace context
in ~/.openclaw/simulation_data/llm-pspice/ to prevent context overflow.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_monaco import st_monaco
from circuit_builder import CircuitBuilder
from llm_orchestrator import LLMOrchestrator
from app_logger import get_logger, log_empty, log_simulation_error, log_invalid_circuit, log_api_error, log_timeout, log_no_code_block, log_syntax_error, log_response_duplication
from sim_config import get_data_dir, get_simulation_dir
import expert_mode
from datetime import datetime
import io
import sys
import os
import json
import requests

# API key storage file
API_KEY_FILE = "saved_api_keys.json"

def save_api_key(provider, key):
    """Save API key to file"""
    try:
        keys = {}
        if os.path.exists(API_KEY_FILE):
            with open(API_KEY_FILE, 'r') as f:
                keys = json.load(f)

        keys[provider] = key

        with open(API_KEY_FILE, 'w') as f:
            json.dump(keys, f)

        return True
    except Exception as e:
        print(f"Error saving API key: {e}")
        return False

def load_api_key(provider):
    """Load API key from file"""
    try:
        if os.path.exists(API_KEY_FILE):
            with open(API_KEY_FILE, 'r') as f:
                keys = json.load(f)
                return keys.get(provider, None)
        return None
    except Exception as e:
        print(f"Error loading API key: {e}")
        return None

def get_cloud_models(api_key):
    """Fetch available models from Ollama Cloud"""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        response = requests.get("https://api.ollama.com/api/tags", headers=headers, timeout=10)

        if response.status_code == 200:
            result = response.json()
            models = result.get("models", [])
            return [m["name"] for m in models]
        return []
    except Exception as e:
        print(f"Error fetching cloud models: {e}")
        return []

def get_local_models():
    """Fetch downloaded models from local Ollama"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)

        if response.status_code == 200:
            result = response.json()
            models = result.get("models", [])
            return [m["name"] for m in models]
        return []
    except Exception as e:
        print(f"Error fetching local models: {e}")
        return []

def save_simulation_data(data, results):
    """
    Automatically save simulation data to disk (outside workspace context)

    Args:
        data: Pandas DataFrame with simulation results
        results: Dictionary with simulation metadata

    Returns:
        str: Path to saved CSV file
    """
    try:
        data_dir = get_data_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}.csv"
        filepath = os.path.join(data_dir, filename)

        # Save CSV
        data.to_csv(filepath, index=False)

        # Also save metadata if available
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "data_points": len(data),
            "variables": list(data.columns),
            "simulation_id": timestamp
        }

        if 'data' in results:
            metadata.update({
                "has_data": True,
                "data_length": len(results['data'])
            })

        metadata_file = os.path.join(data_dir, f"{timestamp}_metadata.json")
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"[INFO] Simulation data saved to {filepath}")
        print(f"[INFO] Metadata saved to {metadata_file}")

        return filepath
    except Exception as e:
        print(f"[ERROR] Failed to save simulation data: {e}")
        return None

# Page configuration
st.set_page_config(
    page_title="LLM Circuit Simulator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []  # For LLM API context (role, content)
if 'circuit_code' not in st.session_state:
    st.session_state.circuit_code = None
if 'editor_code' not in st.session_state:
    st.session_state.editor_code = ""  # Code in Monaco editor (source of truth for simulation)
if 'last_simulated_code' not in st.session_state:
    st.session_state.last_simulated_code = None  # Successfully simulated code (after fixes)
if 'simulation_results' not in st.session_state:
    st.session_state.simulation_results = None
if 'circuit_visualization' not in st.session_state:
    st.session_state.circuit_visualization = None
if 'llm_provider' not in st.session_state:
    st.session_state.llm_provider = "Ollama"
if 'api_key' not in st.session_state:
    st.session_state.api_key = None
if 'ollama_model' not in st.session_state:
    st.session_state.ollama_model = "deepseek-r1:8b"
if 'ollama_api_key' not in st.session_state:
    st.session_state.ollama_api_key = None
if 'openrouter_model' not in st.session_state:
    st.session_state.openrouter_model = "openai/gpt-3.5-turbo"
if 'ollama_use_cloud' not in st.session_state:
    st.session_state.ollama_use_cloud = False
if 'cloud_models' not in st.session_state:
    st.session_state.cloud_models = []
if 'local_models' not in st.session_state:
    st.session_state.local_models = []
if 'use_custom_model' not in st.session_state:
    st.session_state.use_custom_model = False
# Track if user has explicitly selected a model (prevent auto-reset)
if 'user_has_selected_model' not in st.session_state:
    st.session_state.user_has_selected_model = False
# Expert Mode state
if 'expert_mode' not in st.session_state:
    st.session_state.expert_mode = False
if 'expert_pending' not in st.session_state:
    st.session_state.expert_pending = False  # True while waiting for user to press Send
if 'expert_pending_prompt' not in st.session_state:
    st.session_state.expert_pending_prompt = None  # Original user prompt
if 'expert_endpoint_info' not in st.session_state:
    st.session_state.expert_endpoint_info = None
# Track conversation for context
MAX_CHAT_HISTORY = 10  # Keep last 10 turns to manage token usage

st.title("⚡ LLM-Powered Circuit Simulator")
st.markdown("Chat with an LLM to design and simulate electronic circuits")

# Three-tab layout
chat_tab, editor_tab, results_tab = st.tabs(["💬 Chat", "📝 Code Editor", "📊 Simulation Results"])

# Chat interface tab
with chat_tab:
    st.subheader("💬 Chat")

    # Chat history display
    for i, (role, message) in enumerate(st.session_state.chat_history):
        if role == 'user':
            st.chat_message("user").write(message)
        else:
            st.chat_message("assistant").write(message)

    # Show persistent "Run Simulation" button if editor code exists
    if st.session_state.editor_code:
        st.markdown("---")
        if st.button("⚡ Run Simulation", key="chat_run_simulation"):
            st.info("⚙️ Validating circuit and running simulation...")

            with st.spinner("🔍 Validating circuit code..."):
                import time
                time.sleep(0.5)  # Small delay to show validation message

            with st.spinner("⚡ Running Ngspice simulation...\\n(This may take 10-30 seconds depending on circuit complexity)"):
                try:
                    builder = CircuitBuilder()
                    # Run simulation from editor code (source of truth)
                    results = builder.run_simulation(st.session_state.editor_code)
                    st.session_state.simulation_results = results

                    # Enhanced error handling
                    if results.get('error'):
                        # Use enhanced error handler for simulation errors
                        from error_handler import ErrorCategory
                        error_msg = results['error']

                        # Log the simulation error
                        if 'duplicate declaration' in error_msg.lower() or 'ngcomplex' in error_msg.lower():
                            category = ErrorCategory.CIRCUIT_INVALID
                            log_invalid_circuit(
                                prompt="Run Simulation button click",
                                error_message=error_msg,
                                llm_model=st.session_state.ollama_model,
                                provider=st.session_state.llm_provider
                            )
                            st.error(f"❌ Circuit Simulation Error\\n\\n{error_msg}")
                            st.warning("💡 This is a PySpice initialization issue. Try refreshing the page.")
                            st.session_state.chat_history.append(('assistant', f'❌ Simulation failed: {error_msg}'))
                        elif 'convergence' in error_msg.lower() or 'singular' in error_msg.lower():
                            category = ErrorCategory.SIMULATION_FAILED
                            log_simulation_error(
                                prompt="Run Simulation button click",
                                error_message=error_msg,
                                llm_model=st.session_state.ollama_model,
                                provider=st.session_state.llm_provider
                            )
                            st.error(f"❌ Simulation Failed\\n\\n{error_msg}")
                            st.info("💡 Try adjusting component values or simulation parameters.")
                            st.session_state.chat_history.append(('assistant', f'❌ Simulation failed: {error_msg}'))
                        else:
                            log_simulation_error(
                                prompt="Run Simulation button click",
                                error_message=error_msg,
                                llm_model=st.session_state.ollama_model,
                                provider=st.session_state.llm_provider
                            )
                            st.error(f"❌ Simulation error: {error_msg}")
                            st.session_state.chat_history.append(('assistant', f'❌ Simulation failed: {error_msg}'))

                        # Always show technical details for debugging
                        with st.expander("🔧 Technical Details"):
                            st.code(f"Error type: {results.get('error_type', 'Unknown')}\\n\\n{error_msg}", language='text')

                    elif not results.get('data') or len(results['data']) == 0:
                        # Log empty data issue with debug information
                        debug_info = results.get('debug_info', {})
                        log_empty(
                            prompt="Run Simulation button click",
                            llm_model=st.session_state.ollama_model,
                            provider=st.session_state.llm_provider,
                            context="Simulation produced no data",
                            debug_info=debug_info
                        )
                        st.warning("⚠️ Simulation ran but produced no data. This might be due to:")
                        st.warning("- Missing 'analysis = simulator.transient(...)'")
                        st.warning("- Incorrect node names or variables")
                        st.warning("- Simulation parameters (step_time, end_time) may be too small")
                        st.info("💡 Make sure your code defines: circuit + simulator + analysis")
                        st.session_state.chat_history.append(('assistant', '⚠️ Simulation produced no data'))

                    else:
                        st.success(f"✅ Simulation completed! Found {len(results['data'])} data points.")

                        # Show debug info if available and debug mode enabled
                        if st.session_state.get('show_debug_info', False):
                            with st.expander("🔍 Debug Information"):
                                # Show debug info
                                if results.get('debug_info'):
                                    st.subheader("Analysis Object")
                                    debug_info = results['debug_info']
                                    st.json(debug_info)

                                    if not debug_info.get('has_time'):
                                        st.warning("⚠️ Analysis object missing 'time' attribute")
                                    if not debug_info.get('has_nodes'):
                                        st.warning("⚠️ Analysis object missing 'nodes' attribute")

                                # Show filtered circuit code
                                if results.get('filtered_code'):
                                    st.subheader("Filtered Circuit Code (After LLM Fixes)")
                                    with st.empty():
                                        st.code(results['filtered_code'], language='python')

                        # Automatically display circuit if visualization available
                        if results.get('circuit'):
                            st.session_state.circuit_visualization = results['circuit']
                            st.session_state.last_simulated_code = results.get('filtered_code', st.session_state.circuit_code)

                        # Add success message to chat
                        st.session_state.chat_history.append(('assistant', f'✅ Simulation completed! Found {len(results["data"])} data points.'))

                except Exception as e:
                    # Use enhanced error handler for all exceptions
                    from error_handler import handle_llm_error, ErrorCategory
                    error_message = handle_llm_error(e, context="Circuit simulation")

                    # Log the exception
                    error_msg = str(e)
                    if 'timeout' in error_msg.lower():
                        log_timeout(
                            prompt="Run Simulation button click",
                            error_message=error_msg,
                            llm_model=st.session_state.ollama_model,
                            provider=st.session_state.llm_provider
                        )
                    elif 'SyntaxError' in str(type(e)) or 'syntax' in error_msg.lower():
                        log_syntax_error(
                            prompt="Run Simulation button click",
                            error_message=error_msg,
                            llm_response=st.session_state.circuit_code,
                            llm_model=st.session_state.ollama_model,
                            provider=st.session_state.llm_provider
                        )
                    else:
                        log_simulation_error(
                            prompt="Run Simulation button click",
                            error_message=error_msg,
                            llm_model=st.session_state.ollama_model,
                            provider=st.session_state.llm_provider
                        )
                    st.error(f"❌ Error: {error_message}")
                    st.session_state.chat_history.append(('assistant', f'❌ Error: {error_message}'))

            # Rerun to show results
            st.rerun()

    # ── Expert Mode: Launch button (shown when a payload is pending) ──
    if st.session_state.expert_mode and st.session_state.expert_pending:
        st.markdown("---")
        st.warning(f"🔧 **Expert Mode** — Payload waiting on disk. Edit it if needed, then press Launch.")
        st.caption(f"📄 `{expert_mode.PENDING_FILE}`")

        # Show current payload for reference
        with st.expander("👁️ Preview pending payload"):
            try:
                current_payload = expert_mode.load_pending_request()
                st.json(current_payload)
            except Exception as e:
                st.error(f"Could not read payload: {e}")

        col_launch, col_cancel = st.columns(2)
        with col_launch:
            if st.button("🚀 Launch", key="expert_launch", type="primary", use_container_width=True):
                try:
                    payload = expert_mode.load_pending_request()
                    if not isinstance(payload, dict):
                        raise ValueError("Payload must be a JSON object")

                    endpoint_info = st.session_state.expert_endpoint_info or {}
                    provider = st.session_state.llm_provider
                    provider_key = provider.lower().replace(" ", "")

                    # Initialize orchestrator
                    if provider == "Ollama":
                        llm = LLMOrchestrator(
                            provider=provider_key,
                            model_name=st.session_state.ollama_model,
                            use_cloud=st.session_state.ollama_use_cloud,
                            api_key=st.session_state.ollama_api_key if st.session_state.ollama_use_cloud else None
                        )
                    else:
                        model_name = st.session_state.openrouter_model if provider == "OpenRouter" else None
                        llm = LLMOrchestrator(
                            provider=provider_key,
                            api_key=st.session_state.api_key,
                            model_name=model_name
                        )

                    with st.spinner("🚀 Sending expert payload..."):
                        response = llm.send_payload(payload, endpoint_info)

                    # Log to expert-only log
                    entry_num = expert_mode.log_exchange(
                        request_payload=payload,
                        response_text=response,
                        model=payload.get("model", "unknown"),
                        provider=provider,
                        user_prompt=st.session_state.expert_pending_prompt or ""
                    )

                    st.success(f"✅ Expert response received (log entry #{entry_num})")

                    # Feed response back into normal chat flow
                    st.session_state.chat_history.append(('assistant', response))
                    st.session_state.chat_messages.append(('user', st.session_state.expert_pending_prompt or ""))
                    st.session_state.chat_messages.append(('assistant', response))

                    # Parse code blocks like normal flow
                    if '```python' in response and '```' in response:
                        parts = response.split('```')
                        for part in parts:
                            if part.startswith('python'):
                                code = part[6:].strip()
                                st.session_state.circuit_code = code
                                st.session_state.editor_code = code
                                break

                    # Clear pending state
                    st.session_state.expert_pending = False
                    st.session_state.expert_pending_prompt = None
                    st.session_state.expert_endpoint_info = None
                    expert_mode.clear_pending()
                    st.rerun()

                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON in pending_request.json: {e}\n\nFix the file and try again.")
                except Exception as e:
                    st.error(f"❌ Launch failed: {e}")

        with col_cancel:
            if st.button("❌ Cancel", key="expert_cancel", use_container_width=True):
                st.session_state.expert_pending = False
                st.session_state.expert_pending_prompt = None
                st.session_state.expert_endpoint_info = None
                expert_mode.clear_pending()
                st.rerun()

    # User input
    user_input = st.chat_input("Describe the circuit you want to build...")

    if user_input:
        # Add user message to chat (display only)
        st.session_state.chat_history.append(('user', user_input))

        # Get LLM response with progress indicator
        with st.chat_message("assistant"):
            # Determine spinner text based on provider
            provider = st.session_state.llm_provider
            if provider == "Ollama" and st.session_state.ollama_use_cloud:
                spinner_text = f"🔄 Calling Ollama Cloud model: {st.session_state.ollama_model}...\\n(This may take 30-90 seconds)"
                info_text = f"ℹ️ Using cloud model: **{st.session_state.ollama_model}**"
            elif provider == "Ollama":
                spinner_text = f"🔄 Using local Ollama model: {st.session_state.ollama_model}..."
                info_text = f"ℹ️ Using local model: **{st.session_state.ollama_model}**"
            else:
                spinner_text = f"🔄 Calling {provider} API..."
                info_text = f"ℹ️ Using provider: **{provider}**"

            st.info(info_text)

            with st.spinner(spinner_text):
                # Initialize orchestrator with selected provider from session state
                provider = st.session_state.llm_provider
                provider_key = provider.lower().replace(" ", "")

                # Get API key from session state (Ollama doesn't need one for local)
                current_api_key = st.session_state.api_key if provider != "Ollama" else None

                # For Ollama, pass cloud configuration
                if provider == "Ollama":
                    try:
                        llm = LLMOrchestrator(
                            provider=provider_key,
                            model_name=st.session_state.ollama_model,
                            use_cloud=st.session_state.ollama_use_cloud,
                            api_key=st.session_state.ollama_api_key if st.session_state.ollama_use_cloud else None
                        )
                    except Exception as e:
                        st.error(f"Error initializing LLM: {str(e)}")
                        st.markdown("**Debug Info:**")
                        st.code(f"Provider: {provider}\\nUse Cloud: {st.session_state.ollama_use_cloud}\\nModel: {st.session_state.ollama_model}\\nAPI Key: {'Set' if st.session_state.ollama_api_key else 'None'}")
                        st.session_state.chat_history.append(('assistant', f'❌ {str(e)}'))
                        st.session_state.chat_messages.append(('assistant', f'❌ {str(e)}'))
                else:
                    # For OpenRouter, pass the model name
                    model_name = st.session_state.openrouter_model if provider == "OpenRouter" else None
                    llm = LLMOrchestrator(
                        provider=provider_key,
                        api_key=current_api_key,
                        model_name=model_name
                    )

                # Build conversation context for LLM
                chat_messages = []
                if st.session_state.chat_messages:
                    # Trim to last MAX_CHAT_HISTORY turns (excluding current request)
                    chat_messages = st.session_state.chat_messages[-MAX_CHAT_HISTORY:]

                # Add to context if there's a previously simulated circuit
                circuit_context = None
                if st.session_state.last_simulated_code:
                    circuit_context = f"Current working circuit code (successfully simulated):\\n```python\\n{st.session_state.last_simulated_code}\\n```\\n\\nFor modifications, update this code appropriately."

                # ── Expert Mode: save payload to disk and wait for Launch ──
                if st.session_state.expert_mode:
                    # Build payload without sending
                    payload, endpoint_info = llm.build_payload(
                        user_input, chat_history=chat_messages, circuit_context=circuit_context
                    )
                    filepath = expert_mode.save_pending_request(payload)
                    st.session_state.expert_pending = True
                    st.session_state.expert_pending_prompt = user_input
                    st.session_state.expert_endpoint_info = endpoint_info
                    st.info(f"🔧 **Expert Mode:** Payload saved to:\n`{filepath}`\n\nEdit the JSON file if you want, then press **🚀 Launch** below.")
                    st.rerun()

                response = llm.process_request(user_input, chat_history=chat_messages, circuit_context=circuit_context)

                # Log empty response
                if not response or not response.strip():
                    log_empty(
                        prompt=user_input,
                        llm_model=st.session_state.ollama_model if provider == "Ollama" else provider,
                        provider=provider,
                        context="Empty response received from LLM"
                    )
                    st.error("❌ Empty response from LLM. This issue has been logged for debugging.")

                # Parse response to avoid code duplication
                # If response contains python code block, split it: text + code separately
                if '```python' in response and '```' in response:
                    # Extract code blocks and non-code text
                    code_blocks = []
                    parts = response.split('```')
                    non_code_parts = []

                    for i, part in enumerate(parts):
                        if part.startswith('python'):
                            # This is a python code block
                            code = part[6:].strip()
                            code_blocks.append(code)
                        elif part.strip():
                            # Non-code text
                            non_code_parts.append(part)

                    # Write only the non-code text (no markdown code block)
                    if non_code_parts:
                        st.write('\\n'.join(non_code_parts))

                    # Store code for simulation (use first code block only)
                    if code_blocks:
                        circuit_code = code_blocks[0]
                        st.session_state.circuit_code = circuit_code
                        # Also update editor code (source of truth for simulation)
                        st.session_state.editor_code = circuit_code

                        # Show generated code (only once, not duplicated)
                        st.code(circuit_code, language='python')

                        # Add chat history always (before button)
                        st.session_state.chat_history.append(('assistant', response))
                        st.session_state.chat_messages.append(('user', user_input))
                        st.session_state.chat_messages.append(('assistant', response))

                        # Add Run Simulation button (replaced with persistent button)
                        # The Run Simulation button is now shown persistently in the chat history section
                        # when circuit_code exists in session_state
                        st.markdown("---")
                        st.info("💡 Click the 'Run Simulation' button below to simulate this circuit!")

                        # Rerun to show the persistent "Run Simulation" button
                        st.rerun()

# Code Editor tab
with editor_tab:
    st.subheader("📝 Code Editor")

    # Debug: Show if editor_code exists
    debug_mode = st.checkbox("🔍 Debug Mode", value=False)

    if debug_mode:
        if st.session_state.editor_code:
            st.success(f"✅ editor_code exists ({len(st.session_state.editor_code)} chars)")
        else:
            st.warning("⚠️ editor_code is empty")

        # Add test button to manually set code
        test_code = """from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('Test')
circuit.R(1, 'in', 'out', 1 @ u_kOhm)
circuit.C(1, 'out', circuit.gnd, 1 @ u_nF)
simulator = circuit.simulator()
analysis = simulator.transient(step_time=1 @ u_ms, end_time=10 @ u_ms)
"""
        col_test1, col_test2 = st.columns(2)
        with col_test1:
            if st.button("🧪 Set Test Code"):
                st.session_state.editor_code = test_code
                st.success("✅ Set test code in session state")
        with col_test2:
            if st.button("🔄 Rerun Now"):
                st.rerun()

    st.info("💡 Edit the circuit code here and click 'Run Simulation' in the sidebar to execute.")

    # Add Copy Code button
    col_copy, col_info = st.columns([1, 3])
    with col_copy:
        if st.button("📋 Copy Code", help="Copy code to clipboard"):
            if st.session_state.editor_code:
                st.code(st.session_state.editor_code, language='python')
                st.success("✅ Code displayed below! Copy it manually.")
            else:
                st.warning("⚠️ No code to copy.")

    # Monaco editor wrapped in a form to decouple editing from running
    # This prevents lag while typing and ensures the typed value is captured on submit
    with st.form(key="editor_form"):
        editor_code_from_ui = st_monaco(
            value=st.session_state.editor_code,
            language="python",
            height="500px",
        )
        
        # The submit button for the form
        submit_button = st.form_submit_button("💾 Apply Manual Changes", help="Click to save changes before running simulation")

    # Handle the form submission
    if submit_button:
        if editor_code_from_ui is not None:
            st.session_state.editor_code = editor_code_from_ui
            st.session_state.circuit_code = editor_code_from_ui
            st.success("Changes applied! You can now run the simulation from the sidebar or chat tab.")

    # Ensure a default placeholder is present if the editor is completely empty
    if not st.session_state.editor_code or not str(st.session_state.editor_code).strip():
        st.session_state.editor_code = """# Enter circuit code here...
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('RC_Circuit_Verified')
circuit.V('input', 'in', circuit.gnd, 9 @ u_V) # VERIFIED: 9V
circuit.R(1, 'in', 'out', 1 @ u_kOhm)
circuit.C(1, 'out', circuit.gnd, 2 @ u_uF) # VERIFIED: 2uF

simulator = circuit.simulator()
analysis = simulator.transient(step_time=0.1 @ u_ms, end_time=10 @ u_ms)
"""

    # Debug/Automation controls (now AFTER editor is initialized, so editor_code is available)
    if debug_mode:
        st.markdown("### 🎮 Debug Controls")

        # Sync button: Save Monaco editor content to session state
        if st.button("💾 Sync Editor to Session"):
            if editor_code and editor_code.strip():
                st.session_state.editor_code = editor_code
                st.session_state.circuit_code = editor_code
                st.success(f"✅ Saved {len(editor_code)} chars to session state")
            else:
                st.warning("⚠️ Editor is empty")

    # Show current code state below editor (for verification)
    if debug_mode:
        st.markdown("### 🔍 Current `editor_code` content:")
        if st.session_state.editor_code:
            st.code(st.session_state.editor_code, language='python')
        else:
            st.code("(empty)", language='text')

# Simulation results tab
with results_tab:
    st.subheader("📊 Simulation Results")

    if st.session_state.simulation_results:
        # Display results
        results = st.session_state.simulation_results

        if 'plots' in results:
            for plot_data in results['plots']:
                st.pyplot(plot_data)

        if 'data' in results:
            st.subheader("Numerical Data")
            df = pd.DataFrame(results['data'])
            st.dataframe(df)

            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="simulation_results.csv",
                mime="text/csv"
            )

            # Automatically save data to disk (outside workspace context)
            saved_filepath = save_simulation_data(df, results)
            if saved_filepath:
                st.info(f"📁 Data automatically saved to: {saved_filepath}")
                st.caption("Note: Simulation data is stored outside the workspace context.")
    else:
        st.info("💡 Run a circuit simulation in the Chat tab to see results here!")

# Sidebar: Controls and info
with st.sidebar:
    st.header("🎮 Actions")

    # Run Simulation button (always available if there's code in editor)
    if st.session_state.editor_code:
        if st.button(
            "⚡ Run Simulation",
            key="sidebar_run_simulation",
            type="primary",
            use_container_width=True,
            help="Run the circuit code from the Code Editor"
        ):
            # Switch to chat tab to show simulation results
            st.session_state.selected_tab = "Chat"
            st.info("⚙️ Validating circuit and running simulation...")

            with st.spinner("🔍 Validating circuit code..."):
                import time
                time.sleep(0.5)  # Small delay to show validation message

            with st.spinner("⚡ Running Ngspice simulation...\\n(This may take 10-30 seconds depending on circuit complexity)"):
                try:
                    builder = CircuitBuilder()
                    # Run simulation from editor code (source of truth)
                    results = builder.run_simulation(st.session_state.editor_code)
                    st.session_state.simulation_results = results

                    # Enhanced error handling
                    if results.get('error'):
                        error_msg = results['error']

                        # Log the simulation error
                        if 'duplicate declaration' in error_msg.lower() or 'ngcomplex' in error_msg.lower():
                            from error_handler import ErrorCategory
                            log_invalid_circuit(
                                prompt="Sidebar Run Simulation button",
                                error_message=error_msg,
                                llm_model=st.session_state.ollama_model,
                                provider=st.session_state.llm_provider
                            )
                            st.error(f"❌ Circuit Simulation Error\\n\\n{error_msg}")
                            st.warning("💡 This is a PySpice initialization issue. Try refreshing the page.")
                            st.session_state.chat_history.append(('assistant', f'❌ Simulation failed: {error_msg}'))
                        elif 'convergence' in error_msg.lower() or 'singular' in error_msg.lower():
                            from error_handler import ErrorCategory
                            log_simulation_error(
                                prompt="Sidebar Run Simulation button",
                                error_message=error_msg,
                                llm_model=st.session_state.ollama_model,
                                provider=st.session_state.llm_provider
                            )
                            st.error(f"❌ Simulation Failed\\n\\n{error_msg}")
                            st.info("💡 Try adjusting component values or simulation parameters.")
                            st.session_state.chat_history.append(('assistant', f'❌ Simulation failed: {error_msg}'))
                        else:
                            from error_handler import ErrorCategory
                            log_simulation_error(
                                prompt="Sidebar Run Simulation button",
                                error_message=error_msg,
                                llm_model=st.session_state.ollama_model,
                                provider=st.session_state.llm_provider
                            )
                            st.error(f"❌ Simulation error: {error_msg}")
                            st.session_state.chat_history.append(('assistant', f'❌ Simulation failed: {error_msg}'))

                    elif not results.get('data') or len(results['data']) == 0:
                        debug_info = results.get('debug_info', {})
                        log_empty(
                            prompt="Sidebar Run Simulation button",
                            llm_model=st.session_state.ollama_model,
                            provider=st.session_state.llm_provider,
                            context="Simulation produced no data",
                            debug_info=debug_info
                        )
                        st.warning("⚠️ Simulation ran but produced no data.")
                        st.info("💡 Make sure your code defines: circuit + simulator + analysis")
                        st.session_state.chat_history.append(('assistant', '⚠️ Simulation produced no data'))
                    else:
                        st.success(f"✅ Simulation completed! Found {len(results['data'])} data points.")

                        # Automatically display circuit if visualization available
                        if results.get('circuit'):
                            st.session_state.circuit_visualization = results['circuit']
                            st.session_state.last_simulated_code = results.get('filtered_code', st.session_state.editor_code)

                        # Add success message to chat
                        st.session_state.chat_history.append(('assistant', f'✅ Simulation completed! Found {len(results["data"])} data points.'))

                except Exception as e:
                    from error_handler import handle_llm_error, ErrorCategory
                    error_message = handle_llm_error(e, context="Circuit simulation")

                    # Log the exception
                    error_msg = str(e)
                    if 'timeout' in error_msg.lower():
                        log_timeout(
                            prompt="Sidebar Run Simulation button",
                            error_message=error_msg,
                            llm_model=st.session_state.ollama_model,
                            provider=st.session_state.llm_provider
                        )
                    elif 'SyntaxError' in str(type(e)) or 'syntax' in error_msg.lower():
                        log_syntax_error(
                            prompt="Sidebar Run Simulation button",
                            error_message=error_msg,
                            llm_response=st.session_state.editor_code,
                            llm_model=st.session_state.ollama_model,
                            provider=st.session_state.llm_provider
                        )
                    else:
                        log_simulation_error(
                            prompt="Sidebar Run Simulation button",
                            error_message=error_msg,
                            llm_model=st.session_state.ollama_model,
                            provider=st.session_state.llm_provider
                        )
                    st.error(f"❌ Error: {error_message}")
                    st.session_state.chat_history.append(('assistant', f'❌ Error: {error_message}'))

            # Rerun to show results
            st.rerun()
    else:
        st.caption("💡 Generate code in Chat tab to enable simulation")

    st.markdown("---")

    st.header("⚙️ Settings")

    # ── Expert Mode toggle ──
    st.subheader("🔧 Expert Mode")
    expert_toggle = st.checkbox(
        "Enable Expert Mode",
        value=st.session_state.expert_mode,
        help="When ON, the LLM payload is saved to disk before sending. "
             "You can edit the JSON file, then press Launch to send it."
    )
    st.session_state.expert_mode = expert_toggle

    if expert_toggle:
        st.caption(f"Payload file: `expert_mode/pending_request.json`")
        st.caption(f"Log file: `expert_mode/log.json`")

        # Show log count
        log_count = expert_mode.get_log_count()
        if log_count > 0:
            st.info(f"📋 {log_count} expert exchange(s) logged")
            with st.expander("📜 View Expert Log"):
                logs = expert_mode.get_log()
                for i, entry in enumerate(reversed(logs[-10:])):  # Show last 10
                    st.markdown(f"**#{log_count - i}** — {entry.get('timestamp', '?')} — `{entry.get('model', '?')}`")
                    st.caption(f"Prompt: {entry.get('user_prompt', '?')[:100]}...")
                    with st.expander(f"Details #{log_count - i}"):
                        st.json(entry)

    st.markdown("---")

    st.subheader("LLM Configuration")
    provider = st.selectbox(
        "LLM Provider",
        ["OpenAI", "Gemini", "Claude", "DeepSeek", "OpenRouter", "Ollama"],
        index=["OpenAI", "Gemini", "Claude", "DeepSeek", "OpenRouter", "Ollama"].index(st.session_state.llm_provider),
        help="Select your LLM provider"
    )
    st.session_state.llm_provider = provider

    # API key input for providers that need it
    if provider != "Ollama":
        # Load saved API key
        if st.session_state.api_key is None:
            st.session_state.api_key = load_api_key(provider)

        api_key = st.text_input(
            f"{provider} API Key",
            value=st.session_state.api_key,
            type="password",
            help=f"Enter your {provider} API key (saved persistently)"
        )
        # Save to session state and file
        if api_key != st.session_state.api_key:
            st.session_state.api_key = api_key
            if api_key:  # Only save if not empty
                save_api_key(provider, api_key)
        
        # Model selection for OpenRouter (supports many models)
        if provider == "OpenRouter":
            st.subheader("🔀 Model Selection")
            model_help = """
OpenRouter supports hundreds of models. Examples:
- **OpenAI:** openai/gpt-4, openai/gpt-3.5-turbo
- **Anthropic:** anthropic/claude-3.5-sonnet, anthropic/claude-3-opus
- **Google:** google/gemini-2.0-flash-exp, google/gemini-pro
- **Meta:** meta-llama/llama-2-70b-chat, meta-llama/llama-3-70b-instruct
- **DeepSeek:** deepseek/deepseek-r1
- **xAI:** xai/grok-2

See https://openrouter.ai/docs#models for full list.
            """
            
            model_name = st.text_input(
                "Model Name (provider/model-name format)",
                value=st.session_state.openrouter_model,
                help=model_help,
                placeholder="openai/gpt-3.5-turbo"
            )
            if model_name != st.session_state.openrouter_model:
                st.session_state.openrouter_model = model_name
    else:
        st.session_state.api_key = None

        # Ollama configuration
        use_cloud = st.checkbox(
            "Use Ollama Cloud",
            value=st.session_state.ollama_use_cloud,
            help="Enable for cloud models from your Ollama subscription"
        )
        if use_cloud != st.session_state.ollama_use_cloud:
            st.session_state.ollama_use_cloud = use_cloud
            # Clear selected flag when switching modes to allow sensible defaults
            st.session_state.user_has_selected_model = False

        if use_cloud:
            # Load saved Ollama Cloud API key
            if st.session_state.ollama_api_key is None:
                st.session_state.ollama_api_key = load_api_key("ollama_cloud")

            # Cloud API key
            cloud_key = st.text_input(
                "Ollama Cloud API Key",
                value=st.session_state.ollama_api_key,
                type="password",
                help="Your Ollama Cloud API key (from ollama.ai/cloud) - saved persistently"
            )
            if cloud_key != st.session_state.ollama_api_key:
                st.session_state.ollama_api_key = cloud_key
                if cloud_key:  # Only save if not empty
                    save_api_key("ollama_cloud", cloud_key)

            # Fetch and display cloud models
            if cloud_key:
                # Only fetch if we haven't fetched yet or key changed
                if not st.session_state.cloud_models:
                    with st.spinner("Fetching cloud models..."):
                        st.session_state.cloud_models = get_cloud_models(cloud_key)

                if st.session_state.cloud_models:
                    st.success(f"☁️ Found {len(st.session_state.cloud_models)} cloud models in your tier")

                    # Custom model toggle
                    use_custom = st.checkbox("🔧 Use custom model name", value=st.session_state.use_custom_model)
                    st.session_state.use_custom_model = use_custom

                    if use_custom:
                        # Text input for custom model
                        custom_model = st.text_input(
                            "Custom Model Name",
                            value=st.session_state.ollama_model if st.session_state.use_custom_model else "cogito-2.1:671b",
                            help="Enter a custom model name (for models not showing in dropdown)"
                        )
                        if custom_model != st.session_state.ollama_model:
                            st.session_state.ollama_model = custom_model
                            st.session_state.user_has_selected_model = True
                    else:
                        # Dropdown with cloud models
                        # Prioritize models that are known to work
                        recommended_models = [
                            "cogito-2.1:671b",
                            "qwen3-coder:480b",
                            "deepseek-v3.1:671b",
                            "kimi-k2:1t",
                            "nemotron-3-nano:30b"
                        ]

                        # Put recommended first, then the rest
                        sorted_models = []
                        seen = set()

                        for model in recommended_models:
                            if model in st.session_state.cloud_models:
                                sorted_models.append(model)
                                seen.add(model)

                        for model in st.session_state.cloud_models:
                            if model not in seen:
                                sorted_models.append(model)

                        # Find the default index
                        default_index = 0
                        if st.session_state.ollama_model in sorted_models:
                            default_index = sorted_models.index(st.session_state.ollama_model)

                        ollama_model = st.selectbox(
                            "☁️ Select Cloud Model",
                            sorted_models,
                            index=default_index,
                            key="cloud_model_select",  # Unique key to prevent state issues
                            help="Select a model from your Ollama Cloud tier"
                        )
                        if ollama_model != st.session_state.ollama_model:
                            st.session_state.ollama_model = ollama_model
                            st.session_state.user_has_selected_model = True
                else:
                    st.warning("⚠️ Could not fetch cloud models - check your API key")
                    # Only set default model if user hasn't selected one yet
                    if not st.session_state.user_has_selected_model:
                        if st.session_state.ollama_model == "deepseek-r1:8b":
                            st.info("Using recommended model: cogito-2.1:671b")
                            st.session_state.ollama_model = "cogito-2.1:671b"
                        else:
                            st.caption(f"Current model: {st.session_state.ollama_model}")
                    else:
                        st.caption(f"Keeping your selection: {st.session_state.ollama_model}")
            else:
                st.info("🔑 Enter API key to see available cloud models")
        else:
            # Local Ollama
            st.info("🔧 Using local Ollama - Make sure Ollama is running on localhost:11434")

            # Fetch local models
            # Only fetch if we haven't fetched yet
            if not st.session_state.local_models:
                with st.spinner("Fetching local models..."):
                    st.session_state.local_models = get_local_models()

            if st.session_state.local_models:
                st.success(f"💾 Found {len(st.session_state.local_models)} local models")

                # Custom model toggle
                use_custom = st.checkbox("🔧 Use custom model name", value=st.session_state.use_custom_model)
                st.session_state.use_custom_model = use_custom

                if use_custom:
                    # Text input for custom model
                    custom_model = st.text_input(
                        "Custom Model Name",
                        value=st.session_state.ollama_model if st.session_state.use_custom_model else "deepseek-r1:8b",
                        help="Enter a custom model name (for models not showing in dropdown)"
                    )
                    if custom_model != st.session_state.ollama_model:
                        st.session_state.ollama_model = custom_model
                        st.session_state.user_has_selected_model = True
                else:
                    # Dropdown with local models
                    default_index = 0
                    if st.session_state.ollama_model in st.session_state.local_models:
                        default_index = st.session_state.local_models.index(st.session_state.ollama_model)

                    ollama_model = st.selectbox(
                        "💾 Select Local Model",
                        st.session_state.local_models,
                        index=default_index,
                        key="local_model_select",  # Unique key to prevent state issues
                        help="Select a downloaded model from your local Ollama"
                    )
                    if ollama_model != st.session_state.ollama_model:
                        st.session_state.ollama_model = ollama_model
                        st.session_state.user_has_selected_model = True
            else:
                st.warning("⚠️ No local models found or Ollama not running")
                st.info("Try: ollama pull deepseek-r1:8b")
                # Only set default model if user hasn't selected one yet
                if not st.session_state.user_has_selected_model:
                    if st.session_state.ollama_model.startswith("cogito-") or st.session_state.ollama_model.startswith("qwen3-") or st.session_state.ollama_model.startswith("deepseek-v3.1:"):
                        st.session_state.ollama_model = "deepseek-r1:8b"
                    else:
                        st.caption(f"Current model: {st.session_state.ollama_model}")
                else:
                    st.caption(f"Keeping your selection: {st.session_state.ollama_model}")

    st.markdown("---")
    st.markdown("### 📚 Example Queries")
    st.markdown("""
    - "Create a simple RC circuit with R=1kΩ, C=10µF"
    - "Design a voltage divider with 12V input"
    - "Build an LED driver circuit with 5V input"
    - "Simulate a low-pass filter with cutoff 1kHz"
    """)

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    This is a **Proof of Concept** for an LLM-powered circuit simulation environment.

    **Stack:**
    - PySpice + Ngspice (Simulation)
    - Streamlit (UI)
    - LLM (Circuit design)

    **Note:** Issues are automatically logged to `logs/issues.json` for analysis.
    """)

# Clear chat button
if st.button("🗑️ Clear Chat"):
    st.session_state.chat_history = []
    st.session_state.circuit_code = None
    st.session_state.simulation_results = None
    st.rerun()

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
from circuit_builder import CircuitBuilder
from llm_orchestrator import LLMOrchestrator
from app_logger import get_logger, log_empty, log_simulation_error, log_invalid_circuit, log_api_error, log_timeout, log_no_code_block, log_syntax_error, log_response_duplication
from sim_config import get_data_dir, get_simulation_dir
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
if 'circuit_code' not in st.session_state:
    st.session_state.circuit_code = None
if 'simulation_results' not in st.session_state:
    st.session_state.simulation_results = None
if 'circuit_visualization' not in st.session_state:
    st.session_state.circuit_visualization = None
if 'llm_provider' not in st.session_state:
    st.session_state.llm_provider = "OpenAI"
if 'api_key' not in st.session_state:
    st.session_state.api_key = None
if 'ollama_model' not in st.session_state:
    st.session_state.ollama_model = "deepseek-r1:8b"
if 'ollama_api_key' not in st.session_state:
    st.session_state.ollama_api_key = None
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

st.title("⚡ LLM-Powered Circuit Simulator")
st.markdown("Chat with an LLM to design and simulate electronic circuits")

# Two-column layout
col1, col2 = st.columns([1, 1.5])

# Left column: Chat interface
with col1:
    st.subheader("💬 Chat")

    # Chat history display
    for i, (role, message) in enumerate(st.session_state.chat_history):
        if role == 'user':
            st.chat_message("user").write(message)
        else:
            st.chat_message("assistant").write(message)

    # User input
    user_input = st.chat_input("Describe the circuit you want to build...")

    if user_input:
        # Add user message to chat
        st.session_state.chat_history.append(('user', user_input))

        # Get LLM response with progress indicator
        with st.chat_message("assistant"):
            # Determine spinner text based on provider
            provider = st.session_state.llm_provider
            if provider == "Ollama" and st.session_state.ollama_use_cloud:
                spinner_text = f"🔄 Calling Ollama Cloud model: {st.session_state.ollama_model}...\n(This may take 30-90 seconds)"
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
                        st.code(f"Provider: {provider}\nUse Cloud: {st.session_state.ollama_use_cloud}\nModel: {st.session_state.ollama_model}\nAPI Key: {'Set' if st.session_state.ollama_api_key else 'None'}")
                        st.session_state.chat_history.append(('assistant', f'❌ {str(e)}'))
                else:
                    llm = LLMOrchestrator(
                        provider=provider_key,
                        api_key=current_api_key
                    )
                response = llm.process_request(user_input)

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
                        st.write('\n'.join(non_code_parts))

                    # Store code for simulation (use first code block only)
                    if code_blocks:
                        circuit_code = code_blocks[0]
                        st.session_state.circuit_code = circuit_code

                        # Show generated code (only once, not duplicated)
                        st.code(circuit_code, language='python')

                        # Run simulation with progress indicator
                        st.markdown("---")
                        st.info("⚙️ Validating circuit and running simulation...")

                        with st.spinner("🔍 Validating circuit code..."):
                            import time
                            time.sleep(0.5)  # Small delay to show validation message

                        with st.spinner("⚡ Running Ngspice simulation...\n(This may take 10-30 seconds depending on circuit complexity)"):
                            try:
                                builder = CircuitBuilder()
                                results = builder.run_simulation(circuit_code)
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
                                            prompt=user_input,
                                            error_message=error_msg,
                                            llm_model=st.session_state.ollama_model if provider == "Ollama" else provider,
                                            provider=provider
                                        )
                                        st.error(f"❌ Circuit Simulation Error\n\n{error_msg}")
                                        st.warning("💡 This is a PySpice initialization issue. Try refreshing the page.")
                                    elif 'convergence' in error_msg.lower() or 'singular' in error_msg.lower():
                                        category = ErrorCategory.SIMULATION_FAILED
                                        log_simulation_error(
                                            prompt=user_input,
                                            error_message=error_msg,
                                            llm_model=st.session_state.ollama_model if provider == "Ollama" else provider,
                                            provider=provider
                                        )
                                        st.error(f"❌ Simulation Failed\n\n{error_msg}")
                                        st.info("💡 Try adjusting component values or simulation parameters.")
                                    else:
                                        log_simulation_error(
                                            prompt=user_input,
                                            error_message=error_msg,
                                            llm_model=st.session_state.ollama_model if provider == "Ollama" else provider,
                                            provider=provider
                                        )
                                        st.error(f"❌ Simulation error: {error_msg}")

                                    # Always show technical details for debugging
                                    with st.expander("🔧 Technical Details"):
                                        st.code(f"Error type: {results.get('error_type', 'Unknown')}\n\n{error_msg}", language='text')

                                elif not results.get('data') or len(results['data']) == 0:
                                    # Log empty data issue
                                    log_empty(
                                        prompt=user_input,
                                        llm_model=st.session_state.ollama_model if provider == "Ollama" else provider,
                                        provider=provider,
                                        context="Simulation produced no data"
                                    )
                                    st.warning("⚠️ Simulation ran but produced no data. This might be due to:")
                                    st.warning("- Missing 'analysis = simulator.transient(...)'")
                                    st.warning("- Incorrect node names or variables")
                                    st.warning("- Simulation parameters (step_time, end_time) may be too small")
                                    st.info("💡 Make sure your code defines: circuit + simulator + analysis")
                                else:
                                    st.success(f"✅ Simulation completed! Found {len(results['data'])} data points.")

                            except Exception as e:
                                # Use enhanced error handler for all exceptions
                                from error_handler import handle_llm_error, ErrorCategory
                                error_message = handle_llm_error(e, context="Circuit simulation")

                                # Log the exception
                                error_msg = str(e)
                                if 'timeout' in error_msg.lower():
                                    log_timeout(
                                        prompt=user_input,
                                        error_message=error_msg,
                                        llm_model=st.session_state.ollama_model if provider == "Ollama" else provider,
                                        provider=provider
                                    )
                                elif 'SyntaxError' in str(type(e)) or 'syntax' in error_msg.lower():
                                    log_syntax_error(
                                        prompt=user_input,
                                        error_message=error_msg,
                                        llm_response=response,
                                        llm_model=st.session_state.ollama_model if provider == "Ollama" else provider,
                                        provider=provider
                                    )
                                else:
                                    log_simulation_error(
                                        prompt=user_input,
                                        error_message=error_msg,
                                        llm_model=st.session_state.ollama_model if provider == "Ollama" else provider,
                                        provider=provider
                                    )

                                st.error(error_message)

                                with st.expander("🔧 Technical Details"):
                                    st.code(f"Error type: {type(e).__name__}\n\n{str(e)}", language='text')

                    st.session_state.chat_history.append(('assistant', response))
                else:
                    # No code block - just write the response as-is
                    st.write(response)

                    # Log missing code block
                    log_no_code_block(
                        prompt=user_input,
                        llm_response=response,
                        llm_model=st.session_state.ollama_model if provider == "Ollama" else provider,
                        provider=provider
                    )
                    st.warning("⚠️ LLM response doesn't contain Python code block. This issue has been logged.")

                    st.session_state.chat_history.append(('assistant', response))
# Right column: Simulation results
with col2:
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
        st.info("💡 Start chatting on the left to generate and simulate circuits!")

# Sidebar: Controls and info
with st.sidebar:
    st.header("⚙️ Settings")

    st.subheader("LLM Configuration")
    provider = st.selectbox(
        "LLM Provider",
        ["OpenAI", "Gemini", "Claude", "DeepSeek", "Ollama"],
        index=["OpenAI", "Gemini", "Claude", "DeepSeek", "Ollama"].index(st.session_state.llm_provider),
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

    st.subheader("Simulation Settings")
    simulation_time = st.slider("Simulation Time (ms)", 1, 100, 10)
    time_step = st.slider("Time Step (µs)", 0.1, 100.0, 1.0, step=0.1)

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
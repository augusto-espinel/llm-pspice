"""
LLM Orchestrator - Multi-Provider Support
Supports: OpenAI, Google Gemini, Anthropic Claude, DeepSeek, Ollama
"""

import os
from openai import OpenAI
import re
import json
import requests
from error_handler import handle_llm_error, ErrorCategory
from issue_logger import log_api_error, log_timeout

class LLMOrchestrator:
    """
    Orchestrates LLM interactions for circuit design with multi-provider support
    """
    
    def __init__(self, provider="openai", api_key=None, model_name=None, use_cloud=False):
        try:
            self.provider = provider.lower()
            self.api_key = api_key or os.getenv(f'{self.provider.upper()}_API_KEY')
            self.model_name = model_name
            self.use_cloud = use_cloud
            self.client = None
            self._init_client()
        except TypeError as e:
            # Provide more helpful error message
            if 'model_name' in str(e) or 'use_cloud' in str(e):
                raise TypeError(f"LLMOrchestrator initialization error: {str(e)}\n\nThis might be due to Python module caching. Try restarting your Streamlit app.")
            raise
    
    def _init_client(self):
        """Initialize the appropriate client based on provider"""
        try:
            if self.provider == "openai":
                self.client = OpenAI(api_key=self.api_key or os.getenv('OPENAI_API_KEY'))
            elif self.provider == "deepseek":
                self.client = OpenAI(
                    base_url="https://api.deepseek.com",
                    api_key=self.api_key or os.getenv('DEEPSEEK_API_KEY')
                )
            elif self.provider == "ollama":
                if self.use_cloud:
                    # Ollama Cloud - use native API format (not OpenAI-compatible)
                    # /v1/ endpoints don't work with cloud, use /api/ instead
                    base_url = os.getenv('OLLAMA_CLOUD_URL', 'https://api.ollama.com')
                    api_key = self.api_key or os.getenv('OLLAMA_API_KEY')
                    if not api_key:
                        raise ValueError("Ollama Cloud API key required but not provided")

                    # Store cloud configuration for native API calls
                    self.ollama_cloud_base_url = base_url
                    self.ollama_api_key = api_key

                    print(f"DEBUG: Initialized Ollama Cloud (native API)")
                    print(f"DEBUG: Base URL: {base_url}")
                    print(f"DEBUG: API key: {api_key[:20]}...")

                    # Don't initialize OpenAI client - we'll use native requests
                    self.client = None
                else:
                    # Local Ollama uses OpenAI-compatible format
                    self.client = OpenAI(
                        base_url="http://localhost:11434/v1",
                        api_key="not-needed",
                        timeout=30.0
                    )
            # Gemini, Claude use their native clients
            else:
                self.client = None
        except Exception as e:
            raise Exception(f"Failed to initialize {self.provider} client: {str(e)}")
    
    def process_request(self, user_request):
        """
        Process user request and generate circuit code

        Args:
            user_request (str): Natural language description of circuit

        Returns:
            str: LLM response with circuit code
        """
        system_prompt = self._get_system_prompt()

        try:
            # Ollama Cloud uses native API
            if self.provider == "ollama" and self.use_cloud:
                return self._ollama_cloud_request(user_request, system_prompt)
            elif self.provider in ["openai", "deepseek", "ollama"]:
                return self._openai_compatible_request(user_request, system_prompt)
            elif self.provider == "gemini":
                return self._gemini_request(user_request, system_prompt)
            elif self.provider == "claude":
                return self._claude_request(user_request, system_prompt)
            else:
                return self._generate_fallback_code(user_request)
        except Exception as e:
            # Use enhanced error handling
            return handle_llm_error(e, user_request, context=f"LLM request to {self.provider}")
    
    def _openai_compatible_request(self, user_request, system_prompt):
        """Request for OpenAI-compatible APIs (OpenAI, DeepSeek, Ollama)"""
        model_map = {
            "openai": "gpt-3.5-turbo",
            "deepseek": "deepseek-chat",
            "ollama": self.model_name if self.model_name else "llama3"  # Use specified or default model
        }

        model = model_map.get(self.provider, "gpt-3.5-turbo")

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_request}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            return response.choices[0].message.content
        except Exception as e:
            error_msg = str(e)
            print(f"API call failed: {error_msg}")

            # Log the API error
            log_api_error(
                prompt=user_request,
                error_message=error_msg,
                llm_model=model,
                provider=self.provider
            )

            # Help user diagnose connection issues
            if "Connection error" in error_msg or "connection" in error_msg.lower():
                if self.provider == "ollama" and self.use_cloud:
                    return f"❌ Connection error: Couldn't reach Ollama Cloud API.\n\n" \
                           f"Possible issues:\n" \
                           f"• Incorrect base URL (currently trying: api.ollama.ai)\n" \
                           f"• API key might be invalid or expired\n" \
                           f"• Ollama Cloud service might be down\n" \
                           f"• Network connectivity issues\n\n" \
                           f"Try switching to a local model or check:\n" \
                           f"https://ollama.ai/cloud for status\n\n" \
                           f"{self._generate_fallback_code(user_request)}"
                else:
                    return f"❌ Connection error: {error_msg}\n\n{self._generate_fallback_code(user_request)}"

            return f"❌ API Error: {error_msg}\n\n{self._generate_fallback_code(user_request)}"

    def _ollama_cloud_request(self, user_request, system_prompt):
        """Request for Ollama Cloud using native API (not OpenAI-compatible)"""
        import requests
        import time

        model_name = self.model_name if self.model_name else "glm-4.7"

        # Retry logic for cloud requests
        max_retries = 3
        timeout = 120  # Increased from 60 to 120 seconds

        url = f"{self.ollama_cloud_base_url}/api/chat"

        headers = {
            "Authorization": f"Bearer {self.ollama_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_request}
            ],
            "stream": False,
            "options": {
                "num_predict": 1000,  # Limit tokens for faster response
                "temperature": 0.7
            }
        }

        for attempt in range(max_retries):
            try:
                print(f"DEBUG: Ollama Cloud request attempt {attempt + 1}/{max_retries}")
                print(f"DEBUG: URL: {url}")
                print(f"DEBUG: Model: {model_name}")
                print(f"DEBUG: Timeout: {timeout}s")

                response = requests.post(url, json=payload, headers=headers, timeout=timeout)

                if response.status_code == 200:
                    # Parse response - Ollama returns JSON
                    result = response.json()
                    content = result.get("message", {}).get("content", "")

                    if not content:
                        # Try /api/generate as fallback
                        print("DEBUG: Empty response, trying /api/generate")
                        return self._ollama_cloud_generate(user_request, system_prompt)

                    print(f"DEBUG: Success! Response length: {len(content)}")
                    return content
                else:
                    raise Exception(f"Status {response.status_code}: {response.text[:200]}")

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5  # Wait 5s, 10s, 15s
                    print(f"DEBUG: Timeout, waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    # Log timeout
                    log_timeout(
                        prompt=user_request,
                        error_message=f"Request timed out after {max_retries} attempts ({timeout}s each)",
                        llm_model=model_name,
                        provider=f"{self.provider} (cloud)"
                    )
                    raise Exception(f"Request timed out after {max_retries} attempts ({timeout}s each)")

            except Exception as e:
                error_msg = str(e)

                # Log the API error
                log_api_error(
                    prompt=user_request,
                    error_message=error_msg,
                    llm_model=model_name,
                    provider=f"{self.provider} (cloud)"
                )

                if "401" in error_msg or "unauthorized" in error_msg.lower():
                    return f"❌ Unauthorized: Your Ollama Cloud API key is invalid or expired.\n\n" \
                           f"1. Run 'ollama cloud key' to get a new key\n" \
                           f"2. Make sure your subscription is active\n\n" \
                           f"{self._generate_fallback_code(user_request)}"
                elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 5
                        print(f"DEBUG: Connection error, waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return f"❌ Connection error: {error_msg}\n\n" \
                               f"The Ollama Cloud service might be slow or unavailable.\n\n" \
                               f"Suggestions:\n" \
                               f"• Try again in a moment\n" \
                               f"• Use a local model instead (deepseek-r1:8b)\n" \
                               f"• Check Ollama status: https://status.ollama.ai\n\n" \
                               f"{self._generate_fallback_code(user_request)}"

                return f"❌ Ollama Cloud error: {error_msg}\n\n{self._generate_fallback_code(user_request)}"

        return self._generate_fallback_code(user_request)

    def _ollama_cloud_generate(self, user_request, system_prompt):
        """Fallback: Use /api/generate endpoint for Ollama Cloud"""
        import requests
        import time

        model_name = self.model_name if self.model_name else "glm-4.7"

        max_retries = 2
        timeout = 90

        try:
            url = f"{self.ollama_cloud_base_url}/api/generate"

            headers = {
                "Authorization": f"Bearer {self.ollama_api_key}",
                "Content-Type": "application/json"
            }

            # Combine system prompt and user request for generate endpoint
            prompt = f"{system_prompt}\n\nUser: {user_request}"

            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 1000,
                    "temperature": 0.7
                }
            }

            print(f"DEBUG: Trying /api/generate (fallback)")
            print(f"DEBUG: URL: {url}")

            response = requests.post(url, json=payload, headers=headers, timeout=timeout)

            if response.status_code == 200:
                result = response.json()
                content = result.get("response", "")
                print(f"DEBUG: Fallback success! Response length: {len(content)}")
                return content
            else:
                raise Exception(f"Status {response.status_code}: {response.text[:200]}")

        except Exception as e:
            print(f"DEBUG: Fallback failed: {str(e)}")
            raise Exception(f"Generate endpoint failed: {str(e)}")

    def _gemini_request(self, user_request, system_prompt):
        """Request for Google Gemini"""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key or os.getenv('GEMINI_API_KEY'))
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"{system_prompt}\n\nUser: {user_request}"
            response = model.generate_content(prompt)
            
            return response.text
        except ImportError:
            return f"❌ Google Gemini library not installed. Run: pip install google-generativeai\n\n{self._generate_fallback_code(user_request)}"
        except Exception as e:
            return f"❌ Gemini error: {str(e)}\n\n{self._generate_fallback_code(user_request)}"
    
    def _claude_request(self, user_request, system_prompt):
        """Request for Anthropic Claude"""
        try:
            import anthropic
            
            client = anthropic.Anthropic(
                api_key=self.api_key or os.getenv('CLAUDE_API_KEY')
            )
            
            message = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                temperature=0.7,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_request}
                ]
            )
            
            return message.content[0].text
        except ImportError:
            return f"❌ Anthropic library not installed. Run: pip install anthropic\n\n{self._generate_fallback_code(user_request)}"
        except Exception as e:
            return f"❌ Claude error: {str(e)}\n\n{self._generate_fallback_code(user_request)}"
    
    def _get_system_prompt(self):
        """
        System prompt for the LLM (Ralph-improved version)
        """
        return """You are an expert circuit designer and electrical engineer.

Your task is to design electronic circuits based on user requests and generate Python code using PySpice that creates and simulates the circuit.

CRITICAL: You MUST always generate a response with Python code in a ```python``` block.
Never respond with just text - always include working circuit code.


SIMULATION BEST PRACTICES:
1. Include a DC path to ground for every node
2. Use realistic component values (avoid 0 or extremely large values)
3. Set appropriate simulation parameters:
   - step_time: 0.1 to 1 us for typical circuits
   - end_time: 1 to 10 ms to see transient behavior
4. For transient analysis, use pulse sources instead of DC to see charging behavior


IMPORTANT RULES:
1. Use PySpice library symbols:
   - Circuit() - creates a circuit object
   - u_Ohm, u_kOhm - resistance units (note: not u_MOhm)
   - u_V - voltage units
   - u_mA, u_A - current units
   - u_F, u_nF, u_pF - capacitance units (note: not u_uF, use u_nF for nano-farads)
   - u_H - inductance units
   - u_s, u_ms, u_us - time units

2. Circuit components:
   - Circuit.V('name', 'node+', 'node-', voltage @ u_V) - DC voltage source
   - Circuit.PulseVoltageSource('name', 'node+', 'node-', initial_value @ u_V, pulsed_value @ u_V, pulse_width @ u_ms, period @ u_ms, delay_time @ u_ms, rise_time @ u_ms, fall_time @ u_ms) - pulse source for transient analysis
   - Circuit.R('name', 'node+', 'node-', resistance @ u_Ohm) - resistor
   - Circuit.C('name', 'node+', 'node-', capacitance @ u_F) - capacitor
   - Circuit.L('name', 'node+', 'node-', inductance @ u_H) - inductor

3. Simulation:
   - Create simulator: simulator = circuit.simulator()
   - Run analysis: analysis = simulator.transient(step_time=..., end_time=...)
   - Analysis must be stored in variable 'analysis'

4. Code format:
   - Create a 'circuit' variable containing the Circuit object
   - Create an 'analysis' variable containing the simulation results
   - Wrap code in ```python``` block
   - Include comments explaining the circuit

5. Analysis parameters:
   - step_time: Typically 0.1 to 1 us (use @ u_us)
   - end_time: Typically 1 to 10 ms (use @ u_ms)

Example response format:
```python
# RC low-pass filter circuit with pulse source
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('RC_Filter')
# Pulse source: 0V to 10V step, 1ms pulse width, 2ms period
circuit.PulseVoltageSource('input', 'n1', circuit.gnd,
    initial_value=0 @ u_V,
    pulsed_value=10 @ u_V,
    pulse_width=1 @ u_ms,
    period=2 @ u_ms,
    delay_time=0.001 @ u_ms,
    rise_time=0.001 @ u_ms,
    fall_time=0.001 @ u_ms)
circuit.R(1, 'n1', 'n2', 1 @ u_kOhm)
circuit.C(1, 'n2', circuit.gnd, 10 @ u_nF)

simulator = circuit.simulator()
analysis = simulator.transient(step_time=1 @ u_us, end_time=10 @ u_ms)
```

Design safe, practical circuits. If uncertain about values, use common standard values and explain your design choices."""
    
    def _generate_fallback_code(self, user_request):
        """
        Generate fallback code when no API is configured
        """
        request_lower = user_request.lower()
        
        # Check for circuit type
        if 'rc' in request_lower or 'capacitor' in request_lower:
            return """I'll create an RC circuit for you. Since no API key is configured, I'm using a template.

Here's the RC circuit design:

```python
# RC circuit with R=1kΩ, C=10µF
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('RC_Circuit')
circuit.V('input', 'n1', circuit.gnd, 10 @ u_V)
circuit.R(1, 'n1', 'n2', 1 @ u_kOhm)
circuit.C(1, 'n2', circuit.gnd, 10 @ u_F)

simulator = circuit.simulator()
analysis = simulator.transient(step_time=0.1 @ u_ms, end_time=10 @ u_ms)
```

This creates a low-pass RC filter. You can modify the R and C values to adjust the time constant (τ = R×C).
"""
        
        elif 'voltage divider' in request_lower or 'divider' in request_lower:
            return """I'll create a voltage divider for you.

```python
# Voltage divider circuit
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('Voltage_Divider')
circuit.V('input', 'n1', circuit.gnd, 12 @ u_V)
circuit.R(1, 'n1', 'n2', 10 @ u_kOhm)
circuit.R(2, 'n2', circuit.gnd, 10 @ u_kOhm)

analysis = circuit.simulator().transient(step_time=0.1 @ u_ms, end_time=5 @ u_ms)
```

This creates a 50/50 voltage divider. With equal resistors, the output is 6V (half the input).
"""
        
        elif 'led' in request_lower:
            return """I'll create an LED driver circuit for you.

```python
# LED driver circuit with current limiting resistor
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('LED_Driver')
circuit.V('input', 'n1', circuit.gnd, 5 @ u_V)
circuit.R(1, 'n1', 'n2', 220 @ u_Ohm)
# LED modeled as diode (simplified)

simulator = circuit.simulator()
analysis = simulator.transient(step_time=0.1 @ u_ms, end_time=1 @ u_ms)
```

Note: This uses a simplified LED model. For accurate LED simulation, you would need a diode model with appropriate parameters.
"""
        
        else:  # Default: simple resistor circuit
            return """I'll create a simple resistor circuit for you.

```python
# Simple resistor circuit
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('Simple_Resistor')
circuit.V('input', 'n1', circuit.gnd, 10 @ u_V)
circuit.R(1, 'n1', circuit.gnd, 1 @ u_kOhm)

analysis = circuit.simulator().transient(step_time=0.1 @ u_ms, end_time=1 @ u_ms)
```

This is a basic circuit with a voltage source and resistor. For advanced circuit design, configure an API key!
"""


if __name__ == "__main__":
    # Test the orchestrator with different providers
    providers = ["openai", "deepseek", "ollama", "gemini", "claude"]
    
    test_request = "Create a simple RC circuit"
    
    for provider in providers:
        print(f"\nTesting {provider}...")
        try:
            orchestrator = LLMOrchestrator(provider=provider)
            response = orchestrator.process_request(test_request)
            print(f"{provider}: {response[:100]}...")
        except Exception as e:
            print(f"{provider}: Error - {e}")
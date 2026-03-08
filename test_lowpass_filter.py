#!/usr/bin/env python3
"""
Test low-pass filter simulation directly
"""

import sys
sys.path.insert(0, '.')

from circuit_builder import CircuitBuilder
from llm_orchestrator import LLMOrchestrator

# Test the low-pass filter prompt
user_request = "Simulate a low-pass filter with cutoff 1kHz"

print("Testing low-pass filter simulation...")
print("=" * 60)
print(f"Request: {user_request}")
print()

try:
    # Create orchestrator
    orchestrator = LLMOrchestrator()

    # Generate code
    print("Generating code...")
    result = orchestrator.generate_circuit_code(user_request)

    print(f"Result:\n{result}")
    print()

    # If code was generated, try to simulate
    if "```python" in result or "circuit" in result.lower():
        print("Attempting to simulate...")

        builder = CircuitBuilder()

        # Extract code block
        import re
        code_match = re.search(r'```python\n(.*?)\n```', result, re.DOTALL)
        if code_match:
            circuit_code = code_match.group(1)
            print(f"Extracted code:\n{circuit_code}")

            try:
                sim_result = builder.run_simulation(circuit_code)
                print(f"\nSimulation successful!")
                print(f"Data points: {len(sim_result.get('data', []))}")
            except Exception as e:
                print(f"\nSimulation failed:")
                print(f"Error: {e}")
        else:
            print("Could not extract Python code block")
    else:
        print("No code generated")

except Exception as e:
    print(f"Error during test:")
    import traceback
    traceback.print_exc()
    print(f"Error: {e}")
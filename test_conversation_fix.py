"""
Quick test to verify conversation history fixes work.
This tests that the method calls are correct without needing the full Streamlit UI.
"""

import sys
sys.path.insert(0, 'C:\\Users\\augus\\anaconda3\\envs\\pyspice\\lib\\site-packages')

from llm_orchestrator import LLMOrchestrator

# Test 1: Verify method signature accepts chat_history and circuit_context
print("Test 1: Checking LLMOrchestrator.process_request signature...")
import inspect
sig = inspect.signature(LLMOrchestrator.process_request)
params = list(sig.parameters.keys())
print(f"  Parameters: {params}")
assert 'chat_history' in params, "chat_history parameter missing!"
assert 'circuit_context' in params, "circuit_context parameter missing!"
print("  All required parameters present")

# Test 2: Verify we can call process_request with chat_history and circuit_context
print("\nTest 2: Testing process_request call...")
chat_history = [
    ('user', 'Create RC circuit'),
    ('assistant', 'Here is the code')
]
circuit_context = "Current circuit: RC filter"

try:
    llm = LLMOrchestrator(
        provider="ollama",
        model_name="cogito-2.1:671b",
        use_cloud=True,
        api_key="eea0dd8d82c144debbc9bbcfd367b212.ULktML3z6tsOissLTRKGYZT9"
    )

    response = llm.process_request(
        user_request="Change R to 2k",
        chat_history=chat_history,
        circuit_context=circuit_context
    )
    print("  SUCCESS: process_request called with correct parameters!")
    print(f"  Response: {response[:100]}..." if len(response) > 100 else f"  Response: {response}")
except TypeError as e:
    if 'unexpected keyword argument' in str(e):
        print(f"  FAILED: {e}")
        print("  ERROR: This means the parameter name is wrong in the call!")
    else:
        raise
except Exception as e:
    print(f"  Note: API call may fail, but parameter names are correct")
    print(f"  Error: {e}")

print("\nTest complete. If param error occurred above, check that app.py uses:")
print("  llm.process_request(user_input, chat_history=chat_messages, circuit_context=circuit_context)")
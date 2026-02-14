"""
Integration Test - Verifies all systems work together
"""

import sys
import io

# Fix Windows encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("="*70)
print("INTEGRATION TEST - LLM-PSPICE Error Handling")
print("="*70)
print()

# Test 1: Import all modules
print("Test 1: Importing all modules...")
try:
    from error_handler import (
        error_handler,
        ErrorCategory,
        handle_llm_error,
        validate_circuit_code
    )
    print("✅ error_handler module loaded")
except Exception as e:
    print(f"❌ Failed to import error_handler: {e}")
    sys.exit(1)

try:
    from llm_orchestrator import LLMOrchestrator
    print("✅ llm_orchestrator module loaded")
except Exception as e:
    print(f"❌ Failed to import llm_orchestrator: {e}")
    sys.exit(1)

try:
    from circuit_builder import CircuitBuilder
    print("✅ circuit_builder module loaded")
except Exception as e:
    print(f"❌ Failed to import circuit_builder: {e}")
    sys.exit(1)

print()

# Test 2: Error handling integration
print("Test 2: Error handling integration...")
try:
    # Create test error
    test_error = Exception("401 Unauthorized - Invalid API key")
    user_friendly_msg = handle_llm_error(test_error, user_request="Test circuit", context="API call")

    if "Authentication Error" in user_friendly_msg:
        print("✅ Error handler produces user-friendly messages")
    else:
        print("❌ Error handler message missing expected content")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error handling integration failed: {e}")
    sys.exit(1)

print()

# Test 3: Circuit validation integration
print("Test 3: Circuit validation integration...")
try:
    # Valid circuit code
    valid_code = """
circuit = Circuit('Test')
circuit.V('input', 'n1', circuit.gnd, 10 @ u_V)
analysis = circuit.simulator().transient()
"""

    is_valid, error = validate_circuit_code(valid_code)
    if is_valid:
        print("✅ Circuit validation accepts valid code")
    else:
        print(f"❌ Circuit validation incorrectly rejected valid code: {error}")
        sys.exit(1)

    # Invalid circuit code (missing analysis)
    invalid_code = "circuit = Circuit('Test')"
    is_valid, error = validate_circuit_code(invalid_code)
    if not is_valid and "analysis" in error.lower():
        print("✅ Circuit validation catches missing elements")
    else:
        print(f"❌ Circuit validation failed to catch invalid code: {error}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Circuit validation integration failed: {e}")
    sys.exit(1)

print()

# Test 4: Error categorization
print("Test 4: Error categorization...")
test_cases = [
    ("401 unauthorized", "authentication"),
    ("connection timeout", "network"),
    ("request timed out", "timeout"),
    ("model not found", "model_not_found"),
    ("429 too many requests", "rate_limit"),
]

all_passed = True
for error_msg, expected_category in test_cases:
    category = error_handler.categorize_error(error_msg)
    if category.value == expected_category:
        print(f"  ✅ '{error_msg}' -> {category.value}")
    else:
        print(f"  ❌ '{error_msg}' expected {expected_category}, got {category.value}")
        all_passed = False

if not all_passed:
    print("❌ Error categorization test failed")
    sys.exit(1)

print()

# Test 5: Error history tracking
print("Test 5: Error history tracking...")
error_handler.clear_history()
error_handler.get_user_friendly_message("Test error 1", Exception())
error_handler.get_user_friendly_message("Test error 2", Exception())

summary = error_handler.get_error_summary()
if summary['total'] == 2:
    print(f"✅ Error history tracking working (2 errors logged)")
else:
    print(f"❌ Error history tracking failed (expected 2, got {summary['total']})")
    sys.exit(1)

print()

# Final summary
print("="*70)
print("INTEGRATION TEST SUMMARY")
print("="*70)
print()
print("✅ Module imports: All modules loaded successfully")
print("✅ Error handling: Produces user-friendly messages")
print("✅ Circuit validation: Accepts valid and rejects invalid code")
print("✅ Error categorization: Correctly categorizes all test cases")
print("✅ Error tracking: History logging works correctly")
print()
print("🎉 ALL INTEGRATION TESTS PASSED!")
print()
print("The error handling system is fully integrated and operational.")
print("Module dependencies are correctly configured and working together.")
print()
print("="*70)
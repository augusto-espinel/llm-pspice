"""
Test script for the enhanced error handler
Verifies error categorization and user-friendly messages
"""

import sys
import io

# Fix Windows encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from error_handler import error_handler, ErrorCategory, handle_llm_error, validate_circuit_code

def test_error_categorization():
    """Test that errors are correctly categorized"""
    print("="*60)
    print("Testing Error Categorization")
    print("="*60)

    test_cases = [
        ("401 Unauthorized", ErrorCategory.AUTHENTICATION),
        ("Invalid API key", ErrorCategory.AUTHENTICATION),
        ("Connection error: could not reach host", ErrorCategory.NETWORK),
        ("Request timed out", ErrorCategory.TIMEOUT),
        ("Model 'glm-4.7' not found", ErrorCategory.MODEL_NOT_FOUND),
        ("429 Too Many Requests", ErrorCategory.RATE_LIMIT),
        ("Duplicate declaration of struct ngcomplex", ErrorCategory.CIRCUIT_INVALID),
        ("Singular matrix detected", ErrorCategory.SIMULATION_FAILED),
        ("Unknown error occurred", ErrorCategory.UNKNOWN)
    ]

    all_passed = True
    for error_msg, expected_category in test_cases:
        category = error_handler.categorize_error(error_msg)
        status = "✅" if category == expected_category else "❌"
        print(f"{status} '{error_msg[:40]}...': {category.value}")
        if category != expected_category:
            print(f"   Expected: {expected_category.value}, Got: {category.value}")
            all_passed = False

    print()
    return all_passed


def test_user_friendly_messages():
    """Test that user-friendly messages are generated"""
    print("="*60)
    print("Testing User-Friendly Error Messages")
    print("="*60)

    test_errors = [
        (Exception("401 Unauthorized"), "Auth test"),
        (Exception("Connection timeout"), "Network test"),
        (Exception("Model not found"), "Model test")
    ]

    for error, context in test_errors:
        print(f"\n--- Error: {str(error)} ---")
        message = handle_llm_error(error, user_request="Create a circuit", context=context)
        # Show just the first few lines
        lines = message.split('\n')[:5]
        for line in lines:
            print(line)
        print("...")

    print()


def test_circuit_validation():
    """Test circuit code validation"""
    print("="*60)
    print("Testing Circuit Code Validation")
    print("="*60)

    # Valid circuit
    valid_code = """from PySpice.Spice.Netlist import Circuit
circuit = Circuit('Test')
circuit.V('input', 'n1', circuit.gnd, 10 @ u_V)
analysis = circuit.simulator().transient()
"""

    # Missing circuit
    invalid_code_1 = """analysis = simulator.transient()"""

    # Missing analysis
    invalid_code_2 = """circuit = Circuit('Test')"""

    test_cases = [
        (valid_code, True, "Should be valid"),
        (invalid_code_1, False, "Missing circuit definition"),
        (invalid_code_2, False, "Missing analysis")
    ]

    all_passed = True
    for code, should_be_valid, description in test_cases:
        is_valid, error = validate_circuit_code(code)
        status = "✅" if is_valid == should_be_valid else "❌"
        print(f"{status} {description}: {is_valid}")
        if error:
            print(f"   Error: {error[:100]}...")
        if not (is_valid == should_be_valid):
            all_passed = False

    print()
    return all_passed


def test_error_summary():
    """Test error summary functionality"""
    print("="*60)
    print("Testing Error Summary")
    print("="*60)

    # Clear previous history
    error_handler.clear_history()

    # Add some errors
    error_handler.get_user_friendly_message("401 error", Exception(), "Auth context")
    error_handler.get_user_friendly_message("Connection timeout", Exception(), "Network context")
    error_handler.get_user_friendly_message("Model not found", Exception(), "Model context")

    summary = error_handler.get_error_summary()
    print(f"Total errors: {summary['total']}")
    print("By category:")
    for category, count in summary['by_category'].items():
        print(f"  - {category}: {count}")

    print()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("ERROR HANDLER TEST SUITE")
    print("="*60 + "\n")

    results = []

    # Run tests
    results.append(("Error Categorization", test_error_categorization()))
    test_user_friendly_messages()  # Just display, don't check pass/fail
    results.append(("Circuit Validation", test_circuit_validation()))
    test_error_summary()  # Just display, don't check pass/fail

    # Summary
    print("="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(passed for _, passed in results)
    print()
    if all_passed:
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed. See details above.")

    print()
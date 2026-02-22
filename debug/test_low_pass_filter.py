"""
Integration Test: Low-Pass Filter with Cutoff 1kHz

This test runs the complete chain for the failing prompt that's been
causing repeated empty_output issues.

Prompt: "Simulate a low-pass filter with cutoff 1kHz using R=1.59kOhm and C=100nF"

Usage:
    python debug/test_low_pass_filter.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from circuit_builder import CircuitBuilder
from llm_orchestrator import LLMOrchestrator
from error_handler import validate_circuit_code, handle_llm_error


def test_validation():
    """Test the improved validation function"""
    print("=" * 80)
    print("TEST 1: Validation Function")
    print("=" * 80)

    # Test case 1: Bad code - analysis mentioned but not assigned
    bad_code_1 = """
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('Test')
circuit.V('input', 'n1', circuit.gnd, 10 @ u_V)
circuit.R(1, 'n1', 'out', 1 @ u_kOhm)
# TODO: create analysis
analysis = None
"""
    is_valid, error = validate_circuit_code(bad_code_1)
    print("Test 1a - Analysis not assigned:")
    print(f"  Valid: {is_valid}")
    print(f"  Error: {error}")
    print()

    # Test case 2: Bad code - analysis in comment only
    bad_code_2 = """
circuit = Circuit('Test')
circuit.V('input', 'n1', circuit.gnd, 10 @ u_V)
circuit.R(1, 'n1', 'out', 1 @ u_kOhm)
# analysis = simulator.transient(...)
"""
    is_valid, error = validate_circuit_code(bad_code_2)
    print("Test 1b - Analysis in comment only:")
    print(f"  Valid: {is_valid}")
    print(f"  Error: {error}")
    print()

    # Test case 3: Good code - proper assignment
    good_code = """
circuit = Circuit('Test')
circuit.V('input', 'n1', circuit.gnd, 10 @ u_V)
circuit.R(1, 'n1', 'out', 1 @ u_kOhm)
circuit.C(1, 'out', circuit.gnd, 100 @ u_nF)
analysis = circuit.simulator().transient(
    step_time=1 @ u_us,
    end_time=5 @ u_ms
)
"""
    is_valid, error = validate_circuit_code(good_code)
    print("Test 1c - Proper analysis assignment:")
    print(f"  Valid: {is_valid}")
    print(f"  Error: {error}")
    print()


def test_low_pass_filter_circuit():
    """Test the actual low-pass filter circuit"""
    print("=" * 80)
    print("TEST 2: Low-Pass Filter Circuit Simulation")
    print("=" * 80)

    # Simple low-pass filter code (what LLM should generate)
    circuit_code = """
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('RC_LowPass_Filter')

# Input: 10V DC with pulse for transient analysis
circuit.PulseVoltageSource(
    'input',
    'in',
    circuit.gnd,
    initial_value=0 @ u_V,
    pulsed_value=10 @ u_V,
    pulse_width=100 @ u_ms,
    period=100 @ u_ms,
    delay_time=0.001 @ u_ms,
    rise_time=0.001 @ u_ms
)

# RC filter: R=1.59 kOhm, C=100 nF
# Cutoff frequency: fc = 1/(2*pi*R*C) = 1 kHz
circuit.R('1', 'in', 'out', 1.59 @ u_kOhm)
circuit.C('1', 'out', circuit.gnd, 100 @ u_nF)

# Run transient simulation
analysis = circuit.simulator().transient(
    step_time=1 @ u_us,
    end_time=5 @ u_ms
)
"""

    print("Circuit Code:")
    print(circuit_code)
    print()

    # Validate the code
    is_valid, error = validate_circuit_code(circuit_code)
    print("Validation Results:")
    print(f"  Valid: {is_valid}")
    print(f"  Error: {error}")
    print()

    if not is_valid:
        print("ERROR: Circuit code failed validation (BUG!)")
        print()
        return False

    # Run simulation
    print("Running simulation...")
    builder = CircuitBuilder()
    results = builder.run_simulation(circuit_code)

    print("Simulation Results:")
    print(f"  Error: {results.get('error')}")
    print(f"  Data rows: {len(results.get('data', []))}")
    print(f"  Plots: {len(results.get('plots', []))}")
    print()

    # Check debug info
    if results.get('debug_info'):
        print("Debug Info:")
        for key, value in results['debug_info'].items():
            print(f"  {key}: {value}")
        print()

    # Check for issues
    if results.get('error'):
        print("ERROR: Simulation failed with error:")
        print(f"  {results['error']}")
        print()
        return False

    if not results.get('data') or len(results['data']) == 0:
        print("ERROR: Simulation produced NO DATA (empty_output issue!)")
        print()
        print("This indicates a CODE BUG in:")
        print("  - Validation (passed bad code)")
        print("  - Extraction (_extract_analysis_data failed)")
        print("  - Node lookup (wrong node names)")
        print()
        return False

    print("SUCCESS: Simulation successful!")
    print(f"   Generated {len(results['data'])} data points")
    print()
    return True


def test_llm_generation():
    """Test LLM generation for the failing prompt"""
    print("=" * 80)
    print("TEST 3: LLM Generation (Optional - Requires API)")
    print("=" * 80)

    prompt = "Simulate a low-pass filter with cutoff 1kHz using R=1.59kOhm and C=100nF"

    print(f"Prompt: {prompt}")
    print()

    # Note: This requires a working Ollama setup
    # Uncomment to test:
    """
    try:
        orchestrator = LLMOrchestrator()
        response, circuit_code, _ = orchestrator.generate_circuit(prompt)

        print(f"LLM Response:")
        print(response[:500] if len(response) > 500 else response)
        print()

        if circuit_code:
            is_valid, error = validate_circuit_code(circuit_code)
            print(f"Validation: {is_valid}")
            if not is_valid:
                print(f"Error: {error}")
        else:
            print("No circuit code generated")
    except Exception as e:
        print(f"LLM test failed: {e}")
    """

    print("Skipping LLM test (uncomment in code to enable)")
    print()


def run_all_tests():
    """Run all tests"""
    print("\n")
    print("=" * 80)
    print("INTEGRATION TEST SUITE: Low-Pass Filter Debug")
    print("=" * 80)
    print()

    # Test 1: Validation
    test_validation()

    # Test 2: Circuit simulation
    success = test_low_pass_filter_circuit()

    # Test 3: LLM generation (optional)
    test_llm_generation()

    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    if success:
        print("SUCCESS: All tests passed!")
        print()
        print("If the low-pass filter is still failing in the app, the issue is:")
        print("  - LLM generating different code than our test")
        print("  - LLM fixes not being applied correctly")
        print("  - Node name mismatch between LLM and extraction")
        print()
    else:
        print("ERROR: Tests failed - CODE BUG detected!")
        print()
        print("Next steps:")
        print("  1. Check validation logic - should catch bad code")
        print("  2. Check extraction logic - should handle analysis object")
        print("  3. Add debug logging to trace failure point")
        print()


if __name__ == '__main__':
    run_all_tests()
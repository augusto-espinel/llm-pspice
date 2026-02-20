#!/usr/bin/env python3
"""
Unit validator for llm-pspice - fixes common PySpice unit typos
"""

def fix_pyspice_units(code):
    """
    Fix common PySpice unit typos in generated code

    Args:
        code (str): Generated Python code

    Returns:
        str: Code with fixed units
    """
    # Common unit typos and their replacements
    unit_fixes = {
        'u_uF': 'u_nF',          # u_uF doesn't exist, use u_nF for nano-farads
        'u_uf': 'u_nF',          # lowercase version
        'u_MOhm': 'u_kOhm',     # Use kOhm for typical values, or multiply value
        'u_mOhm': 'u_Ohm',      # Common typo
    }

    # Apply fixes
    for bad_unit, good_unit in unit_fixes.items():
        code = code.replace(bad_unit, good_unit)

    return code


if __name__ == '__main__':
    # Test the unit fixer
    test_code = """
    circuit.R(1, 'n1', 'n2', 10 @ u_MOhm)
    circuit.C(1, 'n2', 'n3', 100 @ u_uF)
    code = """
    fixed_code = fix_pyspice_units(test_code)
    print("Original:", test_code)
    print("Fixed:", fixed_code)
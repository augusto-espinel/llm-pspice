def validate_circuit_code(code):
    """
    Validate circuit code before simulation (IMPROVED - 2026-02-22)

    Now checks for actual assignment patterns, not just string matches.

    Args:
        code (str): The circuit code to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    # Improved validation: Check for actual assignment patterns, not just string matches

    # Check for circuit creation
    if 'Circuit(' not in code:
        return False, "Missing circuit creation (Circuit('name'))"

    # Check for circuit assignment (e.g., circuit = Circuit('name'))
    # Use non-comment version (remove comments first)
    code_no_comments = re.sub(r'#.*$', '', code, flags=re.MULTILINE).strip()
    if not re.search(r'circuit\s*=\s*Circuit\(', code_no_comments):
        return False, "Missing circuit assignment (circuit = Circuit('name'))"

    # Check for transient or AC analysis call
    if '.transient(' not in code and '.ac(' not in code:
        return False, "Missing simulation method (.transient() or .ac())"

    # Check for analysis assignment
    # This is the critical check - ensure analysis is assigned, not just mentioned
    # Look for a line that starts with "analysis =" and includes ".transient(" or ".ac(" somewhere after
    code_lines = [line.strip() for line in code.split('\n')]

    analysis_found = False
    for line in code_lines:
        # Skip comment-only lines
        if line.lstrip().startswith('#'):
            continue

        # Remove inline comments for this check
        line_no_inline_comments = re.sub(r'#.*$', '', line).strip()

        # Match: analysis = ... .transient(...) or analysis = ... .ac(...)
        # The pattern is: "analysis" followed by whitespace, "=", whitespace, then any characters including spaces/newlines, then ".transient(" or ".ac("
        if re.match(r'^analysis\s*=\s*.+\.\w+\s*\.\s*(transient|ac)\s*\(', line_no_inline_comments):
            analysis_found = True
            break

    if not analysis_found:
        return False, "Missing analysis assignment (analysis = variable.function().transient(...) or analysis = variable.function().ac(...))"

    # Check for common issues
    issues = []

    # Check for proper unit annotations
    if '@' not in code:
        issues.append("No unit annotations found (use @ u_V, @ u_Ohm, etc.)")

    # Check for ground reference
    if 'gnd' not in code and '0' not in code:  # SPICE allows both gnd and 0
        issues.append("No ground reference found (circuit.gnd or node 0)")

    if issues:
        return False, "Circuit validation issues:\n" + "\n".join(f" • {issue}" for issue in issues)

    return True, None
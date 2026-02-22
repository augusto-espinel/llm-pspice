"""
Complete Chain Analysis Tool

Analyzes issues to determine root cause:
- LLM-related (bad prompt, poor model)
- Code bug (validation, extraction, simulation)
- Hybrid (both)

Usage:
    python analyze_issue_chain.py
"""

import json
import re
from datetime import datetime


def load_issues():
    """Load issues from log file"""
    try:
        with open('logs/issues.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def categorize_issue_root_cause(issue):
    """
    Analyze issue to determine root cause category

    Categories:
    - LLM_ISSUE: Problem is with LLM generation
    - CODE_BUG: Problem is with our code
    - HYBRID: Both LLM and code have issues
    - UNKNOWN: Cannot determine

    Returns:
        dict: {category, confidence, evidence, recommendations}
    """
    issue_type = issue.get('issue_type', 'unknown')
    error_msg = issue.get('error_message', '')
    prompt = issue.get('prompt', '')
    metadata = issue.get('metadata', {})

    evidence = []
    recommendations = []
    confidence = 0.5  # Default medium confidence

    # Check for clear LLM issues
    llm_indicators = {
        'no_code_block': True,
        'empty_llm_response': True,
        'api_error': True,
        'timeout': True
    }

    # Check for clear code bugs
    code_bug_indicators = {
        'duplicate declaration': True,  # Our import filtering failed
        'struct ngcomplex': True,  # Our import filtering failed
        'name.*not defined': True,  # LLM used undefined variable (could be code bug)
        'analysis is None': True,  # Our validation failed
        'Missing required element': True  # Our validation failed
    }

    # Check for potential code bugs in validation
    validation_issues = {
        'Missing required element: analysis': True,  # Validation only checks string match
        'Missing required element: .transient': True,  # Validation checked wrong thing
    }

    # Analyze error message for clues
    llm_clues = 0
    code_bug_clues = 0

    if issue_type in llm_indicators:
        llm_clues += 2

    if issue_type in code_bug_indicators:
        code_bug_clues += 2

    # Check error message patterns
    if error_msg:
        # Code bug patterns
        if 'duplicate declaration' in error_msg.lower():
            code_bug_clues += 2
            evidence.append("ERROR: 'duplicate declaration' - Our import filtering failed to block PySpice imports")
            recommendations.append("🐛 CODE BUG: Fix _filter_pyspice_imports() to properly filter all imports")

        if 'struct ngcomplex' in error_msg.lower():
            code_bug_clues += 2
            evidence.append("ERROR: 'struct ngcomplex' - Our import filtering failed")
            recommendations.append("🐛 CODE BUG: Improve _filter_pyspice_imports() regex pattern")

        if 'name .* is not defined' in error_msg.lower():
            llm_clues += 1
            code_bug_clues += 1
            evidence.append("ERROR: 'name is not defined' - Could be LLM (undefined var) or code bug (missing in namespace)")

        if 'analysis' in error_msg.lower() and 'None' in error_msg:
            code_bug_clues += 2
            evidence.append("ERROR: 'analysis is None' - Our validation passed but analysis was not assigned")
            recommendations.append("🐛 CODE BUG: validate_circuit_code() only checks string 'analysis', doesn't verify assignment")

        if 'Missing required element' in error_msg:
            code_bug_clues += 2
            evidence.append("ERROR: 'Missing required element' - Our validation uses string matching, not actual execution")
            recommendations.append("🐛 CODE BUG: validate_circuit_code() needs runtime validation, not just string matching")

        # LLM patterns
        if 'model not found' in error_msg.lower():
            llm_clues += 2
            evidence.append("ERROR: 'model not found' - LLM model not available (configuration issue, not code bug)")

        if 'timeout' in error_msg.lower():
            llm_clues += 1
            evidence.append("WARNING: 'timeout' - Could be LLM slow OR network issue")

    # Check context for LLM behavior
    context = metadata.get('context', '') or issue.get('context', '')

    if context == 'Simulation produced no data':
        # This is tricky - could be LLM bug OR code bug
        evidence.append("CONTEXT: 'Simulation produced no data' - Code ran but no data extracted")
        evidence.append("   Could be: LLM generated code with wrong node names")
        evidence.append("   Could be: _extract_analysis_data() failed to find nodes")
        recommendations.append("❓ Need to debug: Check filtered_code and analysis object for specific issue")
        confidence = 0.3  # Low confidence without debug info

    # Determine category
    if llm_clues > code_bug_clues * 2:
        category = 'LLM_ISSUE'
        confidence = min(confidence + 0.2, 0.9)
    elif code_bug_clues > llm_clues * 2:
        category = 'CODE_BUG'
        confidence = min(confidence + 0.2, 0.9)
    elif abs(llm_clues - code_bug_clues) <= 1 and llm_clues > 0:
        category = 'HYBRID'
        confidence = 0.6
    else:
        category = 'UNKNOWN'

    # Add LLM-specific recommendations
    if llm_clues > code_bug_clues:
        if issue_type == 'empty_output':
            recommendations.append("🤖 LLM ISSUE: Model returning empty - try different model or improve prompt")
        if 'cogito-2.1' in str(metadata.get('llm_model', '')) and issue_type == 'empty_output':
            recommendations.append("🤖 LLM ISSUE: cogito-2.1:671b frequently returns empty on same prompt")
            recommendations.append("   FIX: Add prompt variety detection to use different models for repeated requests")

    return {
        'category': category,
        'confidence': confidence,
        'llm_clues': llm_clues,
        'code_bug_clues': code_bug_clues,
        'evidence': evidence,
        'recommendations': recommendations
    }


def analyze_recent_issues(limit=10):
    """Analyze recent issues"""
    issues = load_issues()

    if not issues:
        print("No issues found in logs/issues.json")
        return

    # Get recent issues
    recent_issues = issues[-limit:] if len(issues) > limit else issues

    print("=" * 80)
    print("COMPLETE CHAIN ANALYSIS")
    print("=" * 80)
    print(f"Analyzing {len(recent_issues)} recent issues...\n")

    summaries = {
        'CODE_BUG': [],
        'LLM_ISSUE': [],
        'HYBRID': [],
        'UNKNOWN': []
    }

    for i, issue in enumerate(recent_issues, 1):
        print(f"\n{'=' * 80}")
        print(f"Issue #{issue.get('id', '?')} - {issue.get('timestamp', 'Unknown')}")
        print(f"{'=' * 80}")
        print(f"Type: {issue.get('issue_type', 'unknown')}")
        print(f"Prompt: {issue.get('prompt', 'N/A')[:80]}")
        print(f"Model: {issue.get('llm_model', issue.get('metadata', {}).get('llm_model', 'unknown'))}")
        print(f"Error: {issue.get('error_message', '')[:120]}")

        # Analyze root cause
        analysis = categorize_issue_root_cause(issue)

        print(f"\n[ROOT CAUSE ANALYSIS]")
        print(f"   Category: {analysis['category']}")
        print(f"   Confidence: {analysis['confidence']*100:.0f}%")
        print(f"   LLM clues: {analysis['llm_clues']}")
        print(f"   Code bug clues: {analysis['code_bug_clues']}")

        if analysis['evidence']:
            print(f"\n[EVIDENCE]")
            for j, ev in enumerate(analysis['evidence'], 1):
                print(f"   {j}. {ev}")

        if analysis['recommendations']:
            print(f"\n[RECOMMENDATIONS]")
            for rec in analysis['recommendations']:
                print(f"   {rec}")

        summaries[analysis['category']].append(issue.get('prompt', 'N/A')[:50])

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY BY CATEGORY")
    print("=" * 80)

    for category, issues_list in summaries.items():
        if issues_list:
            print(f"\n{category} ({len(issues_list)} issues):")
            for prompt in issues_list:
                print(f"  • {prompt}")


def debug_specific_issue(issue_index=-1):
    """
    Debug a specific issue by analyzing what happened

    Args:
        issue_index: Index of issue (-1 for most recent)
    """
    issues = load_issues()

    if not issues:
        print("No issues found")
        return

    issue = issues[issue_index]

    print("=" * 80)
    print("DEEP DIVE ANALYSIS")
    print("=" * 80)
    print(f"Issue ID: {issue.get('id', '?')}")
    print(f"Timestamp: {issue.get('timestamp', 'Unknown')}")
    print(f"Type: {issue.get('issue_type', 'unknown')}")
    print(f"\nPrompt: {issue.get('prompt', 'N/A')}")
    print(f"\nError Message:")
    print(f"  {issue.get('error_message', 'N/A')}")

    metadata = issue.get('metadata', {})
    if metadata:
        print(f"\nMetadata:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")

    # Analyze
    analysis = categorize_issue_root_cause(issue)

    print(f"\n{'=' * 80}")
    print("ROOT CAUSE DETERMINATION")
    print(f"{'=' * 80}")
    print(f"Primary Category: {analysis['category']}")
    print(f"Confidence: {analysis['confidence']*100:.0f}%")

    if analysis['evidence']:
        print(f"\nEvidence:")
        for i, ev in enumerate(analysis['evidence'], 1):
            print(f"  {i}. {ev}")

    if analysis['recommendations']:
        print(f"\nAction Items:")
        for i, rec in enumerate(analysis['recommendations'], 1):
            print(f"  {i}. {rec}")

    # Additional checks
    if issue.get('issue_type') == 'empty_output':
        print(f"\n{'=' * 80}")
        print("ADDITIONAL CHECKS FOR empty_output")
        print(f"{'=' * 80}")
        print("""
To determine root cause for empty_output:

1. Check if circuit code was generated:
   - If yes but simulation error → Code bug in validation/extraction
   - If yes but no simulation → LLM forgot to add analysis line
   - If empty response → LLM issue (empty response)

2. Check debug output from run_simulation():
   - Look for "Analysis type:", "Time length:", "Available variables"
   - If these printed, extraction failed → Code bug
   - If not printed, simulation failed → LLM issue

3. Recommended fix for debugging:
   - Add breakpoint in circuit_builder.py:227 (run_simulation)
   - Run same prompt with F5
   - Check `filtered_code` variable
   - Check `analysis` variable after exec()
   - Check `_extract_analysis_data(analysis)` return value
""")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--deep-dive':
        # Deep dive on most recent issue
        debug_specific_issue()
    else:
        # Analyze recent issues
        analyze_recent_issues()
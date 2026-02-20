# Ralph Fixer - Issue Tracking and Resolution System

## Overview

Ralph is an automated issue tracking and fixing system for the LLM-PSPICE circuit simulator. It logs all failed prompts, empty outputs, and edge cases, then provides tools to analyze and fix them systematically.

## Features

### 0. **NEW: Ralph Tester (`ralph_tester.py`)** ⭐

**Automated verification that fixes actually work!**

Ralph Tester closes the critical gap between pattern recognition and evidence-based fixes:

**Before:** Ralph analyzes → Generates prompt → Marks "resolved" (never tested)
**After:** Ralph analyzes → Generates prompt → **Ralph Tester verifies** → Mark resolved WITH proof

For each failed prompt:
1. Retries with improved system prompt
2. Runs simulation (minimal, no UI)
3. Records: success/failure + evidence
4. Only marks resolved if tests pass

**Status:** Three categories
- **Success ✅:** Working circuit with data points
- **Failed ❌:** Still fails (same or different error)
- **Inconclusive ⚠️:** Partial improvement or test error

**Usage:** Automatic with Ralph, or standalone with `python test_ralph.py --test-fixes`

**Documentation:** See `RALPH_TESTER_README.md` for complete details

---

### 1. Issue Logging (`issue_logger.py`)

Automatically logs issues when:
- **Empty Outputs**: LLM returns empty or very short response
- **No Code Block**: LLM didn't generate Python code (just text)
- **Simulation Errors**: Circuit fails to simulate (convergence, singular matrix, etc.)
- **Invalid Circuit**: Circuit definition has syntax errors
- **API Errors**: Connection issues, timeouts, authentication failures
- **Timeouts**: Requests timeout after multiple retries
- **Syntax Errors**: Python syntax errors in generated code

Each issue includes:
- Original prompt
- Issue type
- Error message
- LLM response (if any)
- LLM model used
- Provider used
- Timestamp
- Status (open, in_progress, resolved)

### 2. Ralph Fixer (`ralph_fixer.py`)

Analyzes logged issues and applies fixes using multiple strategies:

- **Enhanced System Prompts**: Improves system prompt based on common failures
- **Template-Based Fixes**: Generates circuit templates for common patterns
- **Parameter Guidance**: Adds guidance on simulation parameters
- **Validation Enhancement**: Improves code validation before simulation
- **Fallback Handlers**: Uses pre-defined circuits when LLM fails

### 3. Weekly Automated Fixes (`test_ralph.py`)

Run Ralph weekly to:
- Analyze all open issues
- Identify common failure patterns
- Apply appropriate fixes
- Generate improved system prompts
- Create issue summary reports

## Usage

### Manual Trigger (in App)

1. Open the Streamlit app sidebar
2. Scroll to "🤖 Ralph Fixer (Issue Tracking)"
3. Click "🔄 Run Ralph Analysis"
4. View results and fix summary

### Command Line (Weekly Fix)

```bash
# Weekly fix routine
python test_ralph.py

# Test mode (creates dummy issues)
python test_ralph.py --test
```

### Programmatic Use

```python
from issue_logger import log_empty_output, log_simulation_error
from ralph_fixer import RalphFixer, analyze_and_fix_all_issues

# Log an issue
log_empty_output(
    prompt="Create an RC circuit",
    llm_response="",
    llm_model="glm-4.7",
    provider="ollama"
)

# Analyze and fix all open issues
summary = analyze_and_fix_all_issues()
print(f"Fixed {summary['fixed']} of {summary['total_issues']} issues")
```

## Issue Storage

All issues are stored in JSON format:
- **File**: `logs/issues.json`
- **Format**: Array of issue objects
- **Retention**: All issues kept (resolved issues marked as 'resolved')

## Fix Strategies

### 1. Enhanced System Prompt

When many issues occur, Ralph generates an improved system prompt that:
- Emphasizes the need for Python code blocks
- Adds validation requirements
- Includes simulation best practices
- Provides clearer instructions

**File**: `improved_system_prompt.txt`

To apply:
1. Review `improved_system_prompt.txt`
2. Update `_get_system_prompt()` in `llm_orchestrator.py`
3. Restart the app

### 2. Circuit Templates

For common circuit types, Ralph generates templates:
- RC circuits (filters)
- Voltage dividers
- LED drivers
- RL circuits
- RLC resonant circuits
- Diode rectifiers

**Files**: `template_issue_{id}.py`

Use these as fallbacks or learning examples.

### 3. Parameter Guidance

Ralph identifies cases where simulation parameters caused failures and:
- Recommends appropriate `step_time` values
- Suggests realistic `end_time` values
- Warns about unrealistic component values

### 4. Validation Enhancement

For syntax errors and invalid circuits, Ralph suggests:
- Pre-simulation code validation
- Required element checks
- Unit annotation verification
- Ground reference validation

## Integrating into Workflow

### 1. Automatic Weekly Schedule (Recommended)

Set up a cron job to run Ralph weekly:

```bash
# Weekly Friday at 10 PM
0 22 * * 5 cd /path/to/llm-sim-poc && python test_ralph.py > logs/ralph_weekly.log 2>&1
```

### 2. Manual Trigger After Tests

After testing new prompts or models:
1. Run the app and test various circuits
2. Issues are automatically logged
3. Click "🔄 Run Ralph Analysis" in sidebar
4. Review fixes and apply improved prompts

### 3. Issue Review and Action

1. Check issue summary in sidebar
2. Click "📊 View Issue Details" for specifics
3. Run Ralph analysis
4. Review generated fixes
5. Apply system prompt improvements
6. Test again with same prompts

## Debugging Failed Prompts

When a prompt fails, search the issue log:

```bash
# View all issues
python -c "import json; print(json.dumps(json.load(open('logs/issues.json')), indent=2))"

# Search for specific prompt patterns
grep -A 10 "RC circuit" logs/issues.json
```

Use Ralph's analysis to understand:
- **Root Cause**: Why the LLM failed
- **Fix Strategy**: How to prevent similar failures
- **Template**: Working example for this circuit type

## Monitoring Issue Trends

Track issue patterns over time:

```python
from issue_logger import get_issue_logger

logger = get_issue_logger()
summary = logger.get_issue_summary()

print(f"Total issues: {summary['total']}")
print(f"By type: {summary['by_type']}")
print(f"By model: {summary['by_model']}")
```

Common patterns to watch:
- High `empty_output` → System prompt needs improvement
- High `no_code_block` -> LLM not understanding coding requirement
- Model-specific issues → Consider using different models
- `simulation_error` spikes → Check circuit validation logic

## Example Workflow

### Scenario: User reports "Test prompt failed"

1. **Check issue log**:
   ```python
   python test_ralph.py
   ```

2. **Review output**:
   ```
   📊 Issue Summary:
      Total: 3
      Open: 3
      By Type:
         no_code_block: 2
         simulation_error: 1
   ```

3. **Run Ralph analysis**:
   - Ralph analyzes each issue
   - Generates improved system prompt
   - Creates templates for specific circuits

4. **Apply fixes**:
   - Review `improved_system_prompt.txt`
   - Update `llm_orchestrator.py` if needed
   - Test with same prompts

5. **Verify fix**:
   - Run app
   - Use same prompts
   - Check if issues are resolved

6. **Mark resolved**:
   ```python
   from issue_logger import get_issue_logger
   logger = get_issue_logger()
   logger.mark_resolved(issue_id, "Applied improved system prompt")
   ```

## Technical Details

### Issue Categories

| Type | Description | Common Causes |
|------|-------------|---------------|
| `empty_output` | Empty or very short response | API limits, model capability, prompt ambiguity |
| `no_code_block` | No Python code in response | LLM misunderstood task |
| `simulation_error` | Simulation failed | Missing ground, unrealistic values, convergence issues |
| `invalid_circuit` | Invalid circuit definition | Missing elements, syntax errors |
| `api_error` | API connectivity issue | Network problems, auth failures |
| `timeout` | Request timed out | Slow model, network issues |
| `syntax_error` | Python syntax error | LLM generated invalid code |

### Fix Strategy Selection

Ralph selects fix strategy based on:
1. **Issue type** (e.g., `empty_output` → `enhanced_system_prompt`)
2. **Frequency** (repeated issues get higher priority)
3. **Model patterns** (model-specific failures get tailored fixes)
4. **Prompt similarity** (similar prompts get template-based fixes)

### System Prompt Enhancement

Enhanced prompts add:
- **Mandatory code blocks**: "You MUST always generate Python code in ```python``` block"
- **Validation requirements**: "Always use circuit.gnd, define analysis variable"
- **Parameter guidance**: "Use step_time 0.1-1 µs, end_time 1-10 ms"
- **Error recovery**: "If uncertain, use this template: ..."

## Future Enhancements

Planned features:
- [ ] Auto-apply system prompts after user confirmation
- [ ] Integration with GitHub issues for tracking
- [ ] Automated testing of generated circuits
- [ ] Model comparison (which models fail least)
- [ ] Statistical trend analysis
- [ ] Integration with LLM feedback loops

## Contributing

When adding new issue types or fix strategies:

1. Update `IssueType` enum in `issue_logger.py`
2. Add logging function in `issue_logger.py` (e.g., `log_new_issue_type()`)
3. Add analysis logic in `RalphFixer._analyze_issue()`
4. Add fix strategy in `RalphFixer.apply_fix()`
5. Update documentation

## License

Part of LLM-PSPICE project. See main project license.
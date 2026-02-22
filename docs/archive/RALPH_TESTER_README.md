# Ralph Tester - Automated Verification Module

## Overview

Ralph Tester is an automated testing module that verifies Ralph's proposed improvements actually work before marking issues as resolved. This closes the critical gap between **pattern recognition** and **evidence-based fixes**.

## What It Does

**Before Ralph Tester:**
```
❌ Failed prompt → Ralph analyzes → Generates improved prompt → Marks "resolved"
   (But never tests if it actually works!)
```

**With Ralph Tester:**
```
❌ Failed prompt → Ralph analyzes → Generates improved prompt
    ↓
🧪 Ralph Tester: Retries with improved prompt + runs simulation
    ↓
✅ Evidence: "Now generates working RC circuit with 850 data points"
→ Mark issue resolved WITH proof
```

## Key Features

### 1. Automated Testing Loop

For each failed prompt:
1. Load the improved system prompt
2. Retest the original prompt with LLM
3. Extract generated circuit code
4. Run simulation (minimal, no UI)
5. Record: success/failure + evidence

### 2. Evidence Generation

**Successful tests:**
- Data points generated (e.g., "850 data points")
- Simulation completed successfully
- Output plots available
- Evidence saved to issue log

**Failed tests:**
- Same error as before (fix didn't work)
- Different error (partial improvement)
- Testing error (inconclusive)

### 3. Three Test Categories

| Status | Meaning | Action |
|--------|---------|--------|
| **success** | Works perfectly | Mark resolved with evidence |
| **failed** | Still fails | Keep open, try different fix |
| **inconclusive** | Partial/no improvement | Keep open, needs investigation |

## Integration with Ralph Fixer

### Workflow

```python
# Ralph generated improved prompt
improved_prompt = fixer.generate_improved_system_prompt(issues)

# Ralph Tester automatically runs
from ralph_tester import RalphTester
tester = RalphTester()
test_results = tester.test_improved_prompt(improved_prompt, open_issue_ids)

# Only mark resolved if tests pass
if test_results['successful'] > 0:
    # Mark issues resolved with evidence
    evidence = f"Tested {n} prompts, {m} work ({rate}% success)"
    logger.mark_resolved(issue_id, f"Applied fix | Evidence: {evidence}")
```

### Test Results in Issue Log

Each resolved issue now includes test evidence:

```json
{
  "id": 7,
  "status": "resolved",
  "resolution": "Applied fix: enhanced_system_prompt | Evidence: Tested 3 prompts, 2 now work (66.7% success)",
  "resolved_at": "2026-02-16T00:45:00Z"
}
```

## Usage

### 1. Automatic (with Ralph)

```bash
# Ralph automatically runs tests when applying system prompt fixes
cd C:\Users\augus\.openclaw\workspace\llm-sim-poc
python test_ralph.py

# Output includes:
# [Ralph] Testing improved prompt against 3 failed prompts...
# [Ralph] ✅ Test Results:
# [Ralph]   Total tested: 3
# [Ralph]   Successful: 2
# [Ralph]   Success rate: 66.7%
```

### 2. Manual Standalone Testing

```bash
# Test existing improved prompt
python test_ralph.py --test-fixes

# Tests all open issues and generates report
```

### 3. Programmatic Use

```python
from ralph_tester import RalphTester
from issue_logger import get_issue_logger

logger = get_issue_logger()
tester = RalphTester(logger)

# Test specific improved prompt
with open('improved_system_prompt.txt', 'r') as f:
    improved_prompt = f.read()

# Test specific issues
results = tester.test_improved_prompt(
    improved_prompt_text=improved_prompt,
    issues_to_test=[1, 2, 3]  # Issue IDs to test
)

print(f"Success rate: {results['success_rate']}")
```

## Test Output

### Console Output

```
[RalphTester] Testing improved prompt against failed prompts...
[RalphTester] Testing issue #3: Create a simple circuit...
  ollama - deepseek-r1:8b
  [RalphTester] Getting LLM response...
  [RalphTester] Running circuit simulation...
  ✅ SUCCESS: ✅ Working circuit! Simulation ran successfully with 850 data points

[RalphTester] Testing issue #7: Create an RC circuit...
  ollama - glm-4.7
  [RalphTester] Getting LLM response...
  [RalphTester] Running circuit simulation...
  ✅ SUCCESS: ✅ Working circuit! Simulation ran successfully with 1200 data points

[RalphTester] Test Summary:
  Total: 3
  Successful: 2
  Failed: 1
  Inconclusive: 0
  Success Rate: 66.7%
```

### Test Results File

Saved to `logs/ralph_test_results.json`:

```json
[
  {
    "issue_id": 3,
    "status": "success",
    "reason": "✅ Working circuit! Simulation ran successfully with 850 data points",
    "prompt": "Create a simple circuit",
    "llm_response": "# Simple resistor circuit\nfrom PySpice...",
    "simulation_result": {
      "data_points": 850,
      "has_plots": true
    },
    "evidence": "Generated 850 simulation data points, plots available"
  },
  {
    "issue_id": 7,
    "status": "success",
    "reason": "✅ Working circuit! Simulation ran successfully with 1200 data points",
    ...
  }
]
```

## What Gets Tested

For each issue:
1. **Original prompt** (what user typed)
2. **With improved system prompt** (Ralph's fix)
3. **LLM generates circuit code**
4. **Circuit builder runs simulation**
5. **Checks:** Empty output? No code block? Simulation error? Data produced?

## Test Categories Explained

### Success ✅

- LLM generated valid Python code
- Code ran through circuit builder
- Simulation completed
- **Evidence:** Number of data points, plot availability

### Failed ❌

Cases:
- Empty output (same problem)
- No code block (didn't fix)
- Simulation error with same issue
- **Action:** Don't mark resolved

### Inconclusive ⚠️

Cases:
- Different error (partial improvement)
- No data produced
- Test error itself
- **Action:** Keep open, investigate manually

## Performance

- **Fast:** Uses local Ollama (no API delays)
- **Minimal:** Runs simulation without UI/plots
- **Automated:** No manual intervention needed
- **Test time:** ~10-30 seconds per prompt

## Integration Points

### With Ralph Fixer

```python
# In ralph_fixer.py
def _apply_system_prompt_fix(self, test_improvement=True):
    # Generate improved prompt
    improved_prompt = self.generate_improved_system_prompt(issues)

    # Test it automatically
    if test_improvement:
        tester = RalphTester()
        test_results = tester.test_improved_prompt(improved_prompt)

        # Update last_test_evidence for fix_applied
        self.last_test_evidence = f"{test_results['success_rate']} success."
```

### With Issue Logger

```python
# Mark resolved with evidence
logger.mark_resolved(
    issue_id=7,
    resolution=f"Applied fix | Evidence: Tested 3 prompts, 2 work (66.7% success)"
)
```

### With App UI

Sidebar shows:
```
🤖 Ralph Fixer (Issue Tracking)
   Total: 7
   Open: 3

[🔄 Run Ralph Analysis]

Latest test results:
   Issue #7: ✅ Fixed (Tested: 2/3 success)
   Issue #3: ✅ Fixed (Tested: 2/3 success)
```

## Benefits

1. **Evidence-based fixes** - No more guessing
2. **Confidence** - Test results prove improvements work
3. **Verification** - Catch fixes that don't help
4. **Transparency** - Full test evidence in logs
5. **Continuous learning** - Track success rates over time

## Limitations

1. **Local testing only** - Uses local Ollama, not original provider
2. **No UI validation** - Doesn't check plot quality
3. **Model-dependent** - Test assumes local model behaves like cloud
4. **Time cost** - Adds 10-30s per prompt to Ralph runtime

## Future Enhancements

- [ ] Parallel testing (multiple prompts at once)
- [ ] UI validation plots
- [ ] Model comparison testing
- [ ] Success rate trends over time
- [ ] Auto-apply if success rate > threshold

## Files

- `ralph_tester.py` - Testing module
- `ralph_fixer.py` - Updated with test integration
- `test_ralph.py` - CLI with `--test-fixes` option
- `logs/ralph_test_results.json` - Test results storage

---

**Status:** ✅ Implemented and integrated with Ralph Fixer
**Documentation:** This file
**Integration:** Automatic when Ralph runs `enhanced_system_prompt` fixes
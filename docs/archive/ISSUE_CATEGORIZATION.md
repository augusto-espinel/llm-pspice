# Issue Categorization - Prompt Issues vs Code Bugs

## Overview

Added intelligent categorization to Ralph Fixer to distinguish between:
- **Prompt issues** 🟢 - LLM output problems Ralph can fix with improved prompts
- **Code bugs** 🔴 - Actual code/infrastructure bugs requiring manual fixes
- **Mixed** 🟡 - Issues needing manual review

## Categorization Logic

### 🟢 Likely Prompt Issue

**Indicators:**
- `empty_output` - LLM returned empty response
- `no_code_block` - LLM didn't generate Python code
- `simulation_error` with "ground" or "gnd" - Missing ground reference (prompt fix)
- Simple prompts that should work but don't

**Ralph can fix:**
- Enhanced system prompts
- Better instructions
- Template-based solutions

### 🔴 Likely Code Bug

**Indicators:**
- `api_error` - Connection/infrastructure issues
- `timeout` - Network/performance issues
- Error messages containing:
  * `ngcomplex`, `duplicate declaration` - PySpice initialization bugs
  * `attributeerror`, `importerror` - Python errors
  * `connection`, `network` - Infrastructure errors
  * `authentication`, `unauthorized` - API config issues

**Needs manual fix:**
- Debug app code
- Fix infrastructure
- Update dependencies
- Fix API configuration

### 🟡 Mixed / Review Needed

**Indicators:**
- `simulation_error` (not ground-related)
- `invalid_circuit`
- `syntax_error` (without obvious system bugs)

**Action:**
- Manual review needed
- Could be prompt issue OR code bug
- Developer decides based on context

## Usage

### View Categorization

```bash
# Run Ralph to see categorization
python test_ralph.py

# Output:
# 🔍 Categorizing 5 open issues...
#
# 📊 Categorization Summary:
#    🟢 Likely Prompt Issues (Ralph can help): 3
#    🔴 Likely Code Bugs (manual fix needed): 1
#    🟡 Mixed/Review Needed: 1
```

### Filter by Category

```bash
# Only fix prompt issues (skip code bugs)
python test_ralph.py --filter-prompt

# Output:
# 🔧 Running Ralph on PROMPT ISSUES ONLY (--filter-prompt flag)
#    Filtered to 3 prompt-related issues
```

### Detailed Analysis

Each issue shows category:

```
------------------------------------------------------------
Issue #12: simulation_error
Prompt: Create a simple circuit
Model: deepseek-r1:8b
Provider: ollama
📌 Category: 🟢 LIKELY PROMPT ISSUE (Ralph can help)

Root Cause: Circuit missing ground reference - needs DC path to ground
Recommendation:
Fix Strategy: enhanced_system_prompt
```

```
------------------------------------------------------------
Issue #13: api_error
Prompt: Create an RC circuit
Model: glm-4.7
Provider: ollama
📌 Category: 🔴 LIKELY CODE BUG (manual fix needed)

Root Cause: API connectivity issue (not a prompt problem)
Recommendation: Retry with different model or use local model
Fix Strategy: fallback
```

## Implementation

### Modified Files

**ralph_fixer.py**
- Added `_categorize_issue()` method
- Categorizes based on issue type, error messages, keywords
- Adds `category` field to analysis result

**test_ralph.py**
- Shows categorization summary before running
- Displays emoji-coded category for each issue
- Added `--filter-prompt` flag to skip code bugs
- Added `--fix-code-bugs` flag for experimental use

### Code Snippet

```python
def _categorize_issue(self, issue_type, llm_response, prompt, error_message):
    """Categorize issue as likely_prompt_issue or likely_code_bug"""

    # Prompt-related issues
    prompt_indicators = ['empty_output', 'no_code_block']

    # Code/infrastructure-related issues
    code_bug_keywords = [
        'ngcomplex', 'duplicate declaration',
        'attributeerror', 'importerror',
        'connection', 'network',
        'authentication', 'unauthorized',
        'timeout'
    ]

    # Categorization logic...
    if issue_type in prompt_indicators:
        return 'likely_prompt_issue'
    elif any(kw in error_message.lower() for kw in code_bug_keywords):
        return 'likely_code_bug'
    else:
        return 'mixed'
```

## Example Scenarios

### Scenario 1: Empty Output
```
Prompt: "Create RC circuit"
Result: Empty response
Category: 🟢 LIKELY PROMPT ISSUE
Action: Ralph can fix with enhanced system prompt
```

### Scenario 2: API Connection Error
```
Prompt: "Build voltage divider"
Result: "Connection timeout"
Category: 🔴 LIKELY CODE BUG
Action: Manual fix - check API config, use local model
```

### Scenario 3: Ground Reference Missing
```
Prompt: "Create simple circuit"
Result: "singular matrix: check connections"
Category: 🟢 LIKELY PROMPT ISSUE
Action: Ralph can fix by adding ground requirement to prompt
```

### Scenario 4: PySpice Init Error
```
Prompt: "Simulate filter"
Result: "duplicate declaration of struct ngcomplex"
Category: 🔴 LIKELY CODE BUG
Action: Manual fix - PySpice initialization issue in app code
```

## Developer Workflow

1. **Run Ralph** with categorization:
   ```bash
   python test_ralph.py
   ```

2. **Review categorization** summary:
   - See which issues Ralph can fix
   - Identify code bugs needing manual attention

3. **Decide strategy:**
   - Use `--filter-prompt` to only fix prompt issues
   - Or manually fix code bugs first
   - Then run Ralph on remaining issues

4. **Apply fixes:**
   - Ralph-g fixes: Apply improved prompts
   - Code bugs: Debug and fix manually in app code

5. **Test and deploy**

## Benefits

1. ✅ **Clear separation** - Prompt issues vs code bugs
2. ✅ **Time-saving** - Don't waste Ralph on code bugs
3. ✅ **Targeted fixes** - Ralph focuses on what it can solve
4. ✅ **Manual review** - Developer decides what to address
5. ✅ **Efficient workflow** - Filter and categorize automatically

## CLI Options

```bash
python test_ralph.py                  # Analyze all issues
python test_ralph.py --filter-prompt  # Only prompt issues
python test_ralph.py --test           # Test mode
python test_ralph.py --test-fixes     # Test improvements
```

## Status

✅ Implemented in ralph_fixer.py
✅ CLI filter option added
✅ Emoji-coded display
✅ Automatic categorization based on error patterns
✅ Ready for use

---

**Documentation:** This file
**Implementation:** ralph_fixer.py _categorize_issue() method
**Usage:** `python test_ralph.py --filter-prompt`
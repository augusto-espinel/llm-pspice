# System Prompt Integration Guide

## Summary

Created **enhanced system prompt (v2)** with explicit constraints for common PySpice API hallucinations.

---

## Issues Addressed

### API Hallucination Issues (6 cases)
These were caused by LLMs hallucinating non-existent PySpice parameters:

1. **ID 47, 49** - `CircuitSimulation.transient() got an unexpected keyword argument 'uic'`
2. **ID 57** - `SinusoidalMixin.__init__() got an unexpected keyword argument 'phase'`
3. **ID 62** - `CircuitSimulation.transient() got an unexpected keyword argument 'initial_condition'`
4. **ID 63** - `Unknown argument initial_voltage=0 V`
5. **ID 67** - `Unknown argument Ron=0.1 Ω`

### Unit Hallucination Issues (need separate fix)
These are unit name errors (not parameter errors):

- **u_hour** → needs conversion to seconds
- **u_deg** → needs removal (degrees don't have units)
- **u_uH, u_mH** - FIXED by adding to namespace (not hallucinations, just missing)

---

## New System Prompt: `system_prompt_v2_api_constraints.txt`

### Key Enhancements

#### 1. 🚨 Explicit Invalid Parameters List
```markdown
❌ `Ron=` - Resistance parameter (doesn't exist on any component)
❌ `initial_voltage=` - Capacitor initial condition (wrong syntax)
❌ `initial_condition=` - Initial conditions (wrong syntax)
❌ `uic=` - Use initial conditions parameter (doesn't exist)
❌ `phase=` - Phase shift parameter (doesn't exist)
```

#### 2. ✅ Correct API Usage Examples
Shows correct syntax for:
- `PulseVoltageSource` (all 7 parameters)
- `SinusoidalVoltageSource` (use `offset` not `phase`)
- Component parameters (no extra arguments)

#### 3. Unit Clarification
Lists all available inductance units:
- `u_mH` - Millihenry
- `u_uH` - Microhenry
- `u_μH` - Microhenry (Greek mu)
- `u_nH` - Nanohenry

#### 4. Time Unit Conversion
```python
# WRONG:
1 @ u_hour          # NameError!
1 @ u_deg           # NameError!

# CORRECT:
3600 @ u_s          # 1 hour = 3600 seconds
float(90.0)         # 90 degrees as plain number
```

---

## Integration Steps

### Step 1: Choose Where to Use the New Prompt

**Option A: Replace Existing Prompt** (`llm_orchestrator.py`)
```python
# Find where system prompt is loaded
PROMPT_FILE = 'system_prompt_v2_api_constraints.txt'  # Change this
```

**Option B: Context-Aware Prompt** (based on issue type)
```python
if issue_category == 'API_HALLUCINATION':
    prompt_file = 'system_prompt_v2_api_constraints.txt'
else:
    prompt_file = 'improved_system_prompt.txt'
```

**Option C: Hybrid Prompt** (combine both)
```python
BASE_PROMPT = load('improved_system_prompt.txt')
API_CONSTRAINTS = load('system_prompt_api_additions.txt')
FULL_PROMPT = BASE_PROMPT + "\n\n" + API_CONSTRAINTS
```

### Step 2: Test the New Prompt

**Test Cases:**

1. **Test 1: Resistor with `Ron=` parameter**
   ```
   Input: "Create a 1k resistor with resistance parameter"
   Expected: Should NOT use `Ron=`
   ```

2. **Test 2: Inductor with `u_hour`**
   ```
   Input: "Simulate for 1 hour"
   Expected: Should convert to `3600 @ u_s`
   ```

3. **Test 3: AC source with `phase=`**
   ```
   Input: "Create sinusoidal source with 90 degree phase"
   Expected: Should use `offset` parameter or plain number
   ```

4. **Test 4: Transient with `uic=`**
   ```
   Input: "Simulate with initial conditions"
   Expected: Should NOT use `uic=` parameter
   ```

### Step 3: Monitor Issue Logs

After integrating, check for:
- ❌ Reduction in API hallucination errors (IDs 47, 49, 57, 62, 63, 67)
- ❌ Reduction in unit errors (u_hour, u_deg)
- ⚠️ Watch for NEW hallucination patterns

---

## Verification Checklist

**Before Integration:**
- [x] New system prompt created (`system_prompt_v2_api_constraints.txt`)
- [x] Example circuits tested
- [x] All invalid parameters listed
- [x] Correct syntax examples provided

**After Integration:**
- [ ] Prompt loaded correctly in `llm_orchestrator.py`
- [ ] Test circuits run successfully
- [ ] Issue logs show reduced errors
- [ ] No new hallucination patterns introduced

---

## Files Modified/Created

1. ✅ `system_prompt_v2_api_constraints.txt` - New enhanced system prompt (5.5KB)
2. 📝 `SYSTEM_PROMPT_INTEGRATION_GUIDE.md` - This guide
3. 📝 `BUG_REPORT_2026-02-25.md` - Previous bug report on unit fixer

---

## Expected Impact

**Before:**
- 15 issues marked as `review_needed` (API hallucinations)
- Common errors: `Ron=`, `phase=`, `uic=`, `initial_voltage=`, `u_hour`, `u_deg`

**After:**
- 5-10 issues should be resolved by enhanced system prompt
- Residual issues may need:
  - Template-based circuit generation
  - Additional validation in `circuit_builder.py`
  - Multiple retry attempts

---

## Next Steps

1. **Integrate the prompt** into `llm_orchestrator.py`
2. **Run test suite** with problematic prompts
3. **Monitor new issues** for 24-48 hours
4. **Adjust constraints** based on new hallucination patterns

---

## Note on Unit Fixes

The unit hallucinations for `u_mH`, `u_uH`, `u_μH` were already fixed by:
- Adding these units to `circuit_builder.py` namespace
- These units EXIST in PySpice, just weren't in the execution namespace

Only these units need automatic conversion:
- `u_hour` → `u_s` (×3600)
- `u_deg` → plain number (remove unit)

Non-existent units need simple replacement:
- `u_MOhm` → `u_kOhm`
- `u_MF` → `u_nF`
- `u_uF` → `u_nF`
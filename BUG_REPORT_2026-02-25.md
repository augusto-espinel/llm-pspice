# Bug Report: Incorrect Unit Fix (2026-02-25)

## Summary
I introduced a bug while trying to fix unit hallucination issues. The bug caused **incorrect value scaling** (1000x error) for inductance units.

## Root Cause Analysis

### What I Assumed (WRONG)
- LLMs were hallucinating `u_uH` and `u_mH` units that don't exist in PySpice
- I needed to replace them with `u_nH` (nano-henry)

### Reality (CORRECT)
- `u_uH`, `u_mH`, `u_μH` **ALL EXIST** in PySpice!
- PySpice provides these inductance units out of the box:
  - `u_uH` = micro-henry
  - `u_mH` = millihenry
  - `u_μH` = micro-henry (Greek mu)
  - `u_nH` = nanohenry

### The Real Problem
The units weren't available in the `namespace` dict when executing LLM code via `exec()`:
```python
namespace = {
    'u_H': u_H,        # Henries available
    # 'u_mH': u_mH,    # Missing!
    # 'u_uH': u_uH,    # Missing!
    # 'u_μH': u_μH,    # Missing!
    # 'u_nH': u_nH,    # Missing!
}
```

Even though `from PySpice.Unit import *` makes them available at module level, the `exec()` call only sees what's in the `namespace` dict.

## My Mistake (Code Changes)

### BEFORE (Wrong Fix) ❌
**unit_validator.py:**
```python
unit_fixes = {
    # ...
    'u_uH': 'u_nH',  # BUG: 10 @ u_uH becomes 10 @ u_nH = 1000x smaller!
    'u_uh': 'u_nH',
}
```

**Impact:**
- `10 @ u_uH` (should be 10 μH) → `10 @ u_nH` (10 nH)
- **Value error: 1000x too small!**
- Resonant frequencies and time constants would be wrong

### AFTER (Correct Fix) ✅
**unit_validator.py:**
```python
unit_fixes = {
    'u_uF': 'u_nF',          # Farads (correct fix)
    'u_uf': 'u_nF',
    'u_MOhm': 'u_kOhm',     # Resistance (correct fix)
    'u_mOhm': u_Ohm',
    # REMOVED: u_uH, u_mH (these exist in PySpice!)
}
```

**circuit_builder.py:**
```python
namespace = {
    # Add ALL inductance units to namespace
    'u_H': u_H,
    'u_mH': u_mH,        # millihenry - ADDED
    'u_uH': u_uH,        # microhenry - ADDED
    'u_μH': u_μH,        # microhenry (Greek mu) - ADDED
    'u_nH': u_nH,        # nanohenry - ADDED
}
```

## Issues Affected

### Wrongly Marked as Resolved (9 issues reverted)
- ID 54, 55, 56: `"name 'u_mH' is not defined"` - **not fixed correctly**
- ID 58, 59: `"name 'u_deg' is not defined"` - **not fixed correctly**
- ID 65: `"name 'u_hour' is not defined"` - **not fixed correctly**
- ID 66, 68, 69: `"name 'u_uH' is not defined"` - **not fixed correctly**

**Correct Status:** These are now OPEN again, pending testing.

### Actually Hallucinated Units (still need fix)
- `u_hour` → convert to `u_s` (×3600)
- `u_deg` → remove from phase parameter

**Not Hallucinated (exist in PySpice):**
- `u_uH`, `u_mH`, `u_μH` - all exist!

## Verification

**Test:**
```python
from PySpice.Unit import *

# All these work at module level:
10 @ u_uH  # 10 μH ✅
10 @ u_mH  # 10 mH ✅
10 @ u_nH  # 10 nH ✅

# These don't exist:
1 @ u_hour  # NameError ❌
1 @ u_deg   # NameError ❌
```

## Lessons Learned

1. **Check if PySpice has the unit first!** Don't assume LLM is hallucinating.
2. **Namespace isolation:** `exec()` only sees what's in the namespace dict, not module-level imports.
3. **Value scaling matters:** Micro (μ) ≠ Nano (n)! 1000x difference!
4. **Test fixes before marking issues resolved**

## Required Testing

These 9 issues need verification that the namespace fix actually resolves them:
- ID 54, 55, 56 (u_mH)
- ID 58, 59 (u_deg - also needs phase removal)
- ID 65 (u_hour - also needs time conversion)
- ID 66, 68, 69 (u_uH)

## Files Modified

1. `unit_validator.py` - Removed incorrect u_uH → u_nH fix
2. `circuit_builder.py` - Added u_mH, u_uH, u_μH, u_nH to namespace

## Status

- ✅ Code fix completed
- ✅ Incorrect resolutions reverted
- ⏳ Pending: Testing with actual circuits
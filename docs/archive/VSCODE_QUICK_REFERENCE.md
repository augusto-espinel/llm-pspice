# VS Code Testing Quick Reference

## Fastest Test (3 commands)

```powershell
# 1. Activate environment
conda activate pyspice

# 2. Paste your code into standalone_test.py (line 37)

# 3. Run test
python standalone_test.py
```

## The 5 Checks Run Automatically

1. ✅ Python syntax validation
2. ✅ PySpice imports check
3. ✅ Unit typo fixing (u_uF ⇒ u_nF, u_MOhm ⇒ u_kOhm)
4. ✅ Circuit object creation
5. ✅ Simulation results verification

## Common Fixes Applied

| Bad Code | Fixed Code | Reason |
|----------|------------|--------|
| `10 @ u_uF` | `10 @ u_nF` | Unit doesn't exist |
| `1 @ u_MOhm` | `1 @ u_kOhm` | Use kOhm instead |
| `circuit.V(...)` | `PulseVoltageSource(...)` | DC hides transient |
| `sim.transient()` | `analysis = sim.transient()` | Must assign to variable |

## VS Code Debug Shortcuts

| Action | Shortcut |
|--------|----------|
| Run file | F5 |
| Toggle breakpoint | F9 |
| Step over | F10 |
| Step into | F11 |
| Variables panel | View → Debug → Variables |

## Key Variables to Inspect

- `namespace['circuit']` - Circuit object (check it exists)
- `namespace['analysis']` - Simulation results
- `analysis.time` - Time axis (check length > 0)
- `analysis.n1`, `analysis.n2` - Node voltages
- `analysis.out` or `analysis.output` - Output signal

## Quick Validation Checklist

Before trusting the code:

- [ ] Python syntax OK (step 1)
- [ ] PySpice imports OK (step 2)
- [ ] Units valid (step 3)
- [ ] Circuit created (step 4)
- [ ] **Analysis has data points (step 5)** ← Most important!

## Troubleshooting Flow

```
Error at step 1 → Syntax error in code
Error at step 2 → Missing PySpice installation → conda activate pyspice
Error at step 3 → Unit typo → Auto-fixed, check output
Error at step 4 → Circuit definition error → Check node names, connections
Error at step 5 → No simulation data → Check source type, parameters
```

## What "SUCCESS" Looks Like

```
[1/5] Checking Python syntax... OK
[2/5] Checking PySpice imports... OK
[3/5] Validating PySpice units... OK (after fixes)
[4/5] Creating circuit object... OK
[5/5] Checking simulation results... OK
    Time points: 100001
    Time range: 0.0 to 0.01

RESULT: ALL CHECKS PASSED ✅
```

## What "FAILURE" Looks Like

```
[3/5] Validating PySpice units... FAILED
    Found invalid units: u_uF, u_MOhm
    Auto-applied fixes to code
    VALIDATION: OK (after fixes)

[5/5] Checking simulation results... WARNING
    No time axis data
    This usually means the simulation didn't run properly

RESULT: FAILED ⚠️
```

## Remember

- **Step 5 is critical**: Even if code executes, simulation must produce data
- **DC sources**: Use PulseVoltageSource for transient analysis
- **Ground path**: Every node must connect to ground eventually
- **Units**: Auto-fixer catches most typos, but u_nF is safest for capacitors
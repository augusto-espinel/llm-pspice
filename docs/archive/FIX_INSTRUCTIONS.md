# LLM-PSPICE Fix Instructions

## Problem Summary

Based on Ralph Tester results (2026-02-16), the llm-pspice app has issues:

1. **Missing Ollama Models**: `glm-4.7`, `deepseek-r1`, `llama3` not available locally
2. **Python 3.13 Compatibility**: PySpice has issues with Python 3.13
   - Error: `duplicate declaration of struct ngcomplex`
   - ngspice library bindings incompatible

## Solution

### Option A: Use Python 3.10 (Recommended) ✅

You have a conda environment `pyspice` with Python 3.10.19 already set up.

**Location**: `C:\Users\augus\anaconda3\envs\pyspice`

**To run the app with correct Python:**

#### Method 1: Using Anaconda Prompt (Recommended)

1. Open Anaconda Prompt
2. Activate environment:
   ```
   conda activate pyspice
   ```
3. Navigate to project:
   ```
   cd C:\Users\augus\.openclaw\workspace\llm-sim-poc
   ```
4. Run the app:
   ```
   streamlit run app.py
   ```

#### Method 2: From PowerShell

```powershell
# Initialize conda for PowerShell (one-time setup)
conda init powershell

# Restart PowerShell, then:
conda activate pyspice
cd C:\Users\augus\.openclaw\workspace\llm-sim-poc
streamlit run app.py
```

#### Method 3: Create Launch Script

Create `run_pyspice.ps1` in the llm-sim-poc directory:

```powershell
# Activate conda environment
& conda activate pyspice

# Check Python version
python --version  # Should show Python 3.10.19

# Run Streamlit
streamlit run app.py
```

Then run: `powershell -ExecutionPolicy Bypass -File run_pyspice.ps1`

### Step 2: Use Cloud Models (Fix Missing Models)

Since local Ollama models aren't available, use the cloud models configured in Streamlit.

**In the Streamlit app:**
1. Select "Cloud" or "Other" provider option
2. The app's API key is already stored in `.streamlit/secrets.toml`
3. Use available cloud models instead of missing Ollama models

**Available Cloud Model Types:**
- OpenAI (GPT-4, GPT-4 Turbo)
- Claude (Anthropic)
- Other cloud providers configured in secrets

### Step 3: Update Model Configuration

If the app has hardcoded model names referencing the missing Ollama models, update them:

Check and update in `app.py` or config files:
- Change `glm-4.7` → available cloud model
- Change `deepseek-r1` → available cloud model
- Change `llama3` → available cloud model

### Step 4: Re-run Ralph Tests (After Fixes)

Once environment is fixed and models are working:

```powershell
# Activate pyspice environment
conda activate pyspice

# Run Ralph to test fixes
cd C:\Users\augus\.openclaw\workspace\llm-sim-poc
python test_ralph.py --test-fixes
```

**Expected Results:**
- Tests should now run without PySpice initialization errors
- Improved system prompt validation should pass
- Success rate should increase from 0% to better results

## Verification

### Check Python Version

```powershell
conda activate pyspice
python --version
# Expected: Python 3.10.19
```

### Check PySpice

```powershell
conda activate pyspice
python -c "import PySpice; print('PySpice version:', PySpice.__version__)"
```

### Test Simple Circuit

```python
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('Test')
circuit.R(1, 'in', 'out', 1 @ u_kOhm)
print("✓ PySpice working!")
```

## Quick Start (One Command)

If conda is in your PATH:
```powershell
conda activate pyspice; cd C:\Users\augus\.openclaw\workspace\llm-sim-poc; streamlit run app.py
```

## Status Checklist

- [ ] Option A confirmed: Use Python 3.10 (pyspice conda env)
- [ ] Activate `pyspice` environment before running app
- [ ] Select cloud models in Streamlit UI
- [ ] Update model names if hardcoded in config
- [ ] Test PySpice in Python 3.10 environment
- [ ] Re-run Ralph: `python test_ralph.py --test-fixes`
- [ ] Verify test results show improved success rate

## Next Steps After Testing

If Ralph tests pass:
1. Apply the improved system prompt from `improved_system_prompt.txt`
2. Update `_get_system_prompt()` in `llm_orchestrator.py`
3. Test with real prompts
4. Monitor `logs/issues.json` for any new issues

---

**Date**: 2026-02-17
**Related**: Ralph Tester results (logs/ralph_test_results.json), RALPH_README.md
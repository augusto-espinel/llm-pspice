# Test Suite - Complete Streamlit Validation

## Quick Start

```powershell
cd llm-sim-poc
.\run_all_tests.bat
```

This will run both tests with ACTUAL simulation.

## What These Tests Do

| Test | Purpose | What It Checks | Expected Result |
|------|---------|----------------|-----------------|
| **test_llm_direct.py** | Code generation | Can LLM generate correct pulse syntax? | Has PulseVoltageSource: TRUE |
| **test_like_streamlit_simulation.py** | **Complete workflow** | Full Streamlit workflow with ACTUAL ngspice simulation | Simulation produces data: TRUE |

## Test 2: The REAL Test

This is **the important test** - it does everything Streamlit does:

### What Test 2 Does

1. **Generate circuit code** (same LLM call as Streamlit)
2. **Extract Python code** from response
3. **Build circuit** using CircuitBuilder
4. **RUN SIMULATION** using ngspice (EXACTLY like Streamlit)
5. **Verify data produced** (check simulation output)
6. **Store raw data** OUTSIDE workspace
7. **Keep summary** in workspace

### Why This Matters

Your Streamlit fails with:
- "Missing required element: analysis"
- "Simulation produced no data"

Test 2 will replicate this EXACT workflow and show you:
- ✅ If code generation works
- ✅ If circuit builds successfully
- ✅ If ngspice simulation runs
- ✅ If simulation produces data
- ✅ Where errors occur

### Expected Results

**If all passes:**
```
✅ COMPLETE TEST PASSED

What this proves:
  1. LLM generates correct circuit code ✅
  2. CircuitBuilder builds circuit correctly ✅
  3. Ngspice simulation runs successfully ✅
  4. Simulation produces valid data ✅
  5. Data stored outside workspace ✅
```

**If simulation fails:**
```
❌ FAIL: Simulation error
Error: [specific error message]

This matches what you see in Streamlit!
```

## Running Tests Individually

```powershell
# Test 1: Code generation only
cd llm-sim-poc
conda activate pyspice
python test_llm_direct.py

# Test 2: Complete simulation
conda activate pyspice
python test_like_streamlit_simulation.py
```

## Data Storage (IMPORTANT!)

### What Gets Stored Where

**Workspace (llm-sim-poc/):**
- `test_1_response.txt` - LLM code generation
- `test_2_simulation_summary.json` - Test 2 summary only
- `streamlit_response.txt` - Full LLM response
- `test_1_output.txt` - Console output
- `test_2_simulation_output.txt` - Console output

**OUTSIDE workspace (~/.openclaw/simulation_data/llm-pspice/):**
- `data/` - Raw simulation JSON data
- `plots/` - Matplotlib plots
- `exports/` - CSV exports

### Example Data Files

```bash
# Raw data (outside workspace)
~/.openclaw/simulation_data/llm-pspice/data/
  └── test_2_simulation_20260219_181500.json
      - Full simulation results
      - All data points
      - Metadata (timestamp, prompt, etc.)

# CSV export (outside workspace)
~/.openclaw/simulation_data/llm-pspice/exports/
  └── test_2_export_20260219_181500.csv
      - Time series data
      - All voltages/currents

# Summary (in workspace)
llm-sim-poc/
  └── test_2_simulation_summary.json
      - Success/failure status
      - Error messages
      - Data point count
      - Links to external data files
```

## Understanding Results

### Test 1 Results

Check `test_1_output.txt`:

```
ANALYSIS:
  Has PulseVoltageSource: True     ← Should be TRUE
  Has WRONG pulse syntax: False     ← Should be FALSE
  Has .transient(): True           ← Should be TRUE
```

**If PASS:** Code generation working ✅

**If FAIL (wrong syntax):** Old system prompt ❌

### Test 2 Results

Check `test_2_simulation_output.txt`:

```
CODE GENERATION ANALYSIS:
  ✓ Has Python code block: True
  ✓ Has PulseVoltageSource: True
  ✓ Has WRONG pulse syntax: False
  ✓ Has analysis: True
  ✓ Has circuit definition: True

SIMULATION RESULTS:
  ✅ SIMULATION SUCCESSFUL
     Data points: 10000
     Plots generated: 1
```

**If ALL PASS:**
- Code generation works ✅
- Circuit builds ✅
- Ngspice runs ✅
- Data produced ✅
- Your Streamlit should work too ✅

**If simulation FAILS:**
- Look at error message
- This matches Streamlit errors exactly
- Identify where in the pipeline it breaks

## Troubleshooting

### Test 1 Fails (wrong syntax)

**Problem:** "Has WRONG pulse syntax: True"

**Solution:**
1. Check llm_orchestrator.py has PulseVoltageSource in prompt
2. Delete .pyc files: `del /s "*.pyc"`
3. Try from fresh terminal

### Test 2 Fails (simulation error)

**Problem:** Simulation produces error

**Common errors:**

1. **"Missing required element: analysis"**
   - LLM didn't generate `.transient()` or `.ac()` call
   - Fix: Check system prompt includes analysis instructions

2. **"Simulation produced no data"**
   - Analysis ran but returned empty results
   - Could be DC source in transient analysis
   - CircuitBuilder should auto-convert DC→PulseVoltageSource

3. **"ngspice exited with error"**
   - Compilation error in generated code
   - May need unit fixes (u_uF → u_nF)
   - CircuitBuilder auto-fixes some typos

**Debug:**
```powershell
# Check what code was generated
type streamlit_response.txt

# Look for specific errors
type test_2_simulation_output.txt | findstr /i error

# Check simulation summary
type test_2_simulation_summary.json
```

### Tests Pass But Streamlit Doesn't

**Problem:** Tests work but Streamlit still fails

**Cause:** Streamlit caching old code/state

**Solution:**
1. Find terminal running Streamlit
2. Press Ctrl+C to stop
3. Wait 2 seconds
4. Restart: `.\run_app.ps1`
5. Refresh browser

## Why I Created These Tests

**Test 1 (original):** Just checked code generation
- Proved improved system prompt works
- But didn't PROVE simulation actually works

**Test 2 (NEW):** Complete workflow validation
- Does EVERYTHING Streamlit does
- Actually runs ngspice simulation
- Verifies data is produced
- Stores data correctly (outside workspace)
- Identifies EXACTLY where errors occur

**The difference:**
- Test 1: "Can generate correct code?"
- Test 2: "Can generate, build, simulate, and produce data?"

Test 2 is the **real test** - it matches Streamlit exactly.

## Technical Details

**What test_2_like_streamlit_simulation.py does:**

```python
# Step 1: Generate code (same as Streamlit)
response = llm.process_request(prompt)

# Step 2: Extract Python code
circuit_code = extract_code(response)

# Step 3: Build and simulate (same as Streamlit)
builder = CircuitBuilder()
sim_results = builder.run_simulation(circuit_code)

# Step 4: Verify results
if sim_results['data']:
    print("✅ Simulation produced data")
else:
    print("❌ Simulation produced no data")

# Step 5: Store data OUTSIDE workspace
data_file = out_of_workspace / "simulation_results.json"
with open(data_file, 'w') as f:
    json.dump(sim_results['data'], f)

# Step 6: Keep summary in workspace
summary_file = Path('test_2_simulation_summary.json')
with open(summary_file, 'w') as f:
    json.dump(summary, f)
```

**Data storage policy:**
- Raw simulation data → `~/.openclaw/simulation_data/llm-pspice/data/`
- CSV exports → `~/.openclaw/simulation_data/llm-pspice/exports/`
- Plots → `~/.openclaw/simulation_data/llm-pspice/plots/`
- Summaries →_workspace

This keeps the workspace light (no large CSV files) while preserving raw data.

## Next Steps

Run the complete test suite!

```powershell
cd llm-sim-poc
.\run_all_tests.bat
```

Then check:
1. `test_1_output.txt` - Code generation
2. `test_2_simulation_output.txt` - Full workflow
3. `test_2_simulation_summary.json` - Summary only
4. Raw data at `~/.openclaw/simulation_data/llm-pspice/`

Send me the output and we'll understand exactly where your Streamlit issue is!
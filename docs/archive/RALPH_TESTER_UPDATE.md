# Ralph Tester Update - Now Uses Streamlit Settings

## What Changed

**Before:** Ralph used `deepseek-r1:8b` (local model) for ALL testing

**After:** Ralph uses the SAME model, provider, and API key as Streamlit app for each test

## How It Works Now

### 1. Reads Original Issue Settings

From `logs/issues.json`, Ralph extracts:
```
{
  "id": 10,
  "prompt": "Simulate a low-pass filter...",
  "llm_model": "cogito-2.1:671b",  ← THIS!
  "provider": "Ollama",            ← THIS!
  "status": "resolved"
}
```

### 2. Determines Cloud/Local

```python
# Cloud models have ":" in name (e.g., cogito-2.1:671b)
is_cloud_model = ':' in original_model and provider == 'ollama'
use_cloud = is_cloud_model
```

### 3. Loads API Key from Streamlit Storage

```python
# From saved_api_keys.json (same as Streamlit app)
api_key = load_api_key('ollama_cloud')
```

**Location:** `saved_api_keys.json` (created when you enter API key in Streamlit app)

```json
{
  "ollama_cloud": "sk-ollama-xxxxxxxxxxxxx"
}
```

### 4. Creates LLM with IDENTICAL Settings

```python
llm = LLMOrchestrator(
    provider='ollama',
    model_name='cogito-2.1:671b',  ← SAME as original!
    use_cloud=True,                ← SAME as original!
    ollama_api_key=api_key         ← SAME as original!
)
```

### 5. Runs Test (Same Workflow as Streamlit)

```python
# 1. Prompt LLM (same as Streamlit app)
response = llm.process_request(prompt)

# 2. Extract Python code (same as Streamlit app)
code_blocks = extract_python_code(response)

# 3. Run CircuitBuilder (same as Streamlit app)
builder = CircuitBuilder()
results = builder.run_simulation(circuit_code)

# 4. Check results (same as Streamlit app)
if results.get('data'):
    return "SUCCESS"
```

## Prerequisites

### 1. OpenAI Module Required

The `llm_orchestrator.py` requires the `openai` module (even for Ollama):

```powershell
conda activate pyspice
pip install openai
```

**Why?** Ollama Cloud uses OpenAI-compatible API, so the orchestrator needs the OpenAI SDK.

### 2. API Key Must Be Saved

The Streamlit app must have saved the API key. Check:

```powershell
type saved_api_keys.json
```

Should contain:
```json
{
  "ollama_cloud": "sk-ollama-xxxxxxxxxxxxx"
}
```

If not present:
1. Start Streamlit app: `.\run_app.ps1`
2. Enter your Ollama Cloud API key in the sidebar
3. Close the app (key is now saved)

## Running Tests

### Quick Test (All Open Issues)

```powershell
conda activate pyspice
python test_ralph.py
```

### Test Specific Issues

```python
from ralph_tester_streamlit_settings import test_improvements

improved_prompt = """You are...[your improved prompt]"""

# Test issue IDs 10, 11, 12
results = test_improvements(improved_prompt, issues_to_test=[10, 11, 12])
```

### Test Only Cloud Models

```python
import json

# Load issues
with open('logs/issues.json', 'r') as f:
    all_issues = json.load(f)

# Filter for cloud models only
cloud_issues = [
    i for i in all_issues
    if ':' in i.get('llm_model', '') and 'status' not in i
]

cloud_ids = [i['id'] for i in cloud_issues]

# Test only cloud model issues
results = test_improvements(improved_prompt, cloud_ids)
```

## Test Results

### Example Output

```
[RalphTester] Testing improved prompt against failed prompts...
[RalphTester] Using same models and API keys as Streamlit app

[RalphTester] Testing issue #10: Simulate a low-pass filter...
  Model:    cogito-2.1:671b
  Provider: ollama
  Use Cloud: True
  [OK] Using Ollama Cloud API key
  [RalphTester] Getting LLM response...
  [RalphTester] Running circuit simulation (same as Streamlit)...
  [OK] SUCCESS: Working circuit! Simulation ran successfully with 100001 data points

[RalphTester] Testing issue #11: Simulate a low-pass filter...
  Model:    cogito-2.1:671b
  Provider: ollama
  Use Cloud: True
  [OK] Using Ollama Cloud API key
  [RalphTester] Getting LLM response...
  [RalphTester] Running circuit simulation (same as Streamlit)...
  [OK] SUCCESS: Working circuit! Simulation ran successfully with 100001 data points

============================================================
[RalphTester] Test Summary:
  Total tested:   2
  Successful:     2 ✅
  Failed:         0 ❌
  Inconclusive:   0 ⚠️
  Success rate:   100.0%
============================================================

Test results saved to logs/ralph_test_results.json
Test report: logs/ralph_test_report.md
```

### Results File

Each test result includes:

```json
{
  "issue_id": 10,
  "original_model": "cogito-2.1:671b",
  "use_cloud": true,
  "status": "success",
  "reason": "Working circuit! Simulation ran successfully with 100001 data points",
  "prompt": "Simulate a low-pass filter...",
  "llm_response": "Here's the PySpice code...",
  "simulation_result": {
    "data_points": 100001,
    "has_plots": true
  },
  "evidence": "Generated 100001 simulation data points using cogito-2.1:671b",
  "tested_with": "cogito-2.1:671b (cloud=true)"
}
```

## Comparison: Before vs After

| Aspect | Before | After |
|--------|--------|-------|
| Model | Always `deepseek-r1:8b` | Same as issue (e.g., `cogito-2.1:671b`) |
| Provider | Always `local` | Same as issue (`cloud`/`local`) |
| API Key | None needed | Loaded from `saved_api_keys.json` |
| Accuracy | Wrong test | **Identical to Streamlit app** ✅ |

## Troubleshooting

### Error: ModuleNotFoundError: No module named 'openai'

```powershell
conda activate pyspice
pip install openai
```

### Error: No Ollama Cloud API key found

```powershell
# Start Streamlit app and enter API key
.\run_app.ps1
# Enter API key in sidebar
# Close app (key saved)
```

### Error: Fallback to local model

```
[WARN] No Ollama Cloud API key found, falling back to local
```

The test will run with `deepseek-r1:8b` (local) instead of the cloud model.

### Want to force local-only testing?

```python
# Modify line 95 in ralph_tester_streamlit_settings.py
use_cloud = False  # Was: is_cloud_model
```

## Files Modified

1. **`ralph_tester_streamlit_settings.py`** - NEW (original: `ralph_tester.py`)
2. **`RALPH_TESTER_UPDATE.md`** - This file

## Next Steps

1. Install openai: `pip install openai`
2. Ensure API key is saved: Start Streamlit app, enter key, close
3. Run tests: `python test_ralph.py`
4. Review results: `type logs\ralph_test_results.json`
5. Read report: `type logs\ralph_test_report.md`

Now Ralph's tests are **TRULY representative** of what will happen in the Streamlit app!
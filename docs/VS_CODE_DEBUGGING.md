# Debugging Streamlit App in VS Code

## Quick Setup (One-Time)

1. **Open Project in VS Code:**
   ```powershell
   cd C:\Users\augus\.openclaw\workspace\llm-sim-poc
   code .
   ```

2. **Install Required Extensions:**
   - Python (Microsoft)
   - Pylance (Microsoft) - for IntelliSense
   - Python Debugger (Microsoft)

3. **Select Correct Python Interpreter:**
   - Press `Ctrl+Shift+P` → "Python: Select Interpreter"
   - Choose the `pyspice` Conda environment:
     ```
     C:\Users\augus\anaconda3\envs\pyspice\python.exe
     ```

---

## Debugging the Streamlit App

### Method 1: Using Debug Configurations (Recommended)

1. **Open Debug View:**
   - Press `Ctrl+Shift+D` or click the Run & Debug icon in the sidebar

2. **Select Configuration:**
   - Choose "Streamlit: Debug App" from the dropdown

3. **Start Debugging:**
   - Press `F5` or click the green play button
   - App launches in integrated terminal
   - Browser opens to `http://localhost:8501`

4. **Set Breakpoints:**
   - Click in the gutter (left margin) next to any line
   - Red dot appears = breakpoint set
   - Common files to debug:
     - `app.py` (UI logic)
     - `circuit_builder.py` (circuit building)
     - `llm_orchestrator.py` (LLM API calls)

5. **Debug Controls:**
   - `F5` - Continue
   - `F10` - Step over
   - `F11` - Step into
   - `Shift+F11` - Step out
   - `Shift+F5` - Stop debugging

---

### Method 2: Debug Existing Streamlit Process

1. **Start Streamlit normally:**
   ```powershell
   conda activate pyspice
   streamlit run app.py
   ```

2. **Attach Debugger:**
   - In VS Code: `Ctrl+Shift+D`
   - Click "create a launch.json file" (if needed)
   - Choose "Python" → "Remote Attach"
   - Port: `5678` (default Python debugger port)

3. **Add to launch.json:**
   ```json
   {
       "name": "Python: Attach",
       "type": "python",
       "request": "attach",
       "connect": {
           "host": "localhost",
           "port": 5678
       }
   }
   ```

---

## Debugging Specific Components

### Debugging Circuit Building (`circuit_builder.py`)

**Set breakpoints at key locations:**

```python
# circuit_builder.py - Line ~227: run_simulation()
def run_simulation(self, circuit_code):
    results = {  # <--- Breakpoint here
        'plots': [],
        'data': None,
        'error': None
    }
    
    # Line ~254: After DC to pulse conversion
    if self.use_pulse_sources:
        filtered_code, num_conversions = self._convert_dc_to_pulse(filtered_code)  # <--- Check conversions
        if num_conversions > 0:
            print(f"\n[INFO] Converted {num_conversions} DC source(s)")
    
    # Line ~278: After LLM fixes applied
    filtered_code = re.sub(r'circuit\.Sinusoidal\(', 'circuit.SinusoidalVoltageSource(', filtered_code)  # <--- Check fixes
    
    # Line ~288: Before executing circuit code
    exec(compile(filtered_code, '<string>', 'exec'), namespace)  # <--- Breakpoint to see final code
    
    # Check variables in DEBUG CONSOLE:
    print("=== Final filtered code ===")
    print(filtered_code)  # See what code will execute
    print("=== Namespace ===")
    print(list(namespace.keys()))  # See what's available
```

### Debugging LLM Calls (`llm_orchestrator.py`)

**Key breakpoints:**

```python
# llm_orchestrator.py
def _ollama_cloud_request(self, user_request, system_prompt):
    # Line ~120: Before API call
    payload = {  # <--- Breakpoint here - see what's being sent
        "model": self.model_name,
        "messages": messages,
        "stream": False
    }
    
    # Line ~125: After response received
    response = requests.post(...)  # <--- Breakpoint here - see response
    print("=== API Response ===")
    print(response.text)
```

### Debugging Error Handling (`error_handler.py`)

**Set breakpoints at error categorization:**

```python
# error_handler.py - Line ~45: handle_llm_error()
def handle_llm_error(e, context="unknown"):
    # Check error category
    category = categorize_error(e)  # <--- Breakpoint here - see what error type
    
    # Line ~65: Log error
    log_api_error(...)  # <--- See what gets logged
```

---

## Using the Debug Console

While debugging, the **DEBUG CONSOLE** (bottom panel) lets you:

1. **Inspect Variables:**
   ```python
   # Type variable names to see their values
   circuit
   filtered_code
   analysis.frequency
   results['data']
   ```

2. **Test Code:**
   ```python
   # Test small snippets without restarting
   len(circuit_code)
   filtered_code.count('SinusoidalVoltageSource')
   type(results['error'])
   ```

3. **Call Functions:**
   ```python
   fix_pyspice_units("test u_uF u_MOhm")
   validate_circuit_code(circuit_code)
   ```

---

## Common Debugging Scenarios

### Scenario 1: Simulation Fails

**Symptoms:** "SIMULATION FAILED" or error returned

**Debug Steps:**

1. **Set breakpoint in `circuit_builder.py` at line ~227** (run_simulation)
2. **Run debug → F5**
3. **When paused, check:**
   ```python
   filtered_code  # See the code being executed
   namespace      # See what's imported/available
   ```
4. **Step through** using F10 to find exact failure point
5. **Check error message** in variables or terminal

**Common Issues:**
- `duplicate declaration` → Check for duplicate imports
- `unit undefined` → PySpice unit not in namespace
- `node name is a Python keyword` → 'in' used as node name

### Scenario 2: LLM Returns Bad Code

**Symptoms:** Generated code has syntax errors

**Debug Steps:**

1. **Set breakpoint in `llm_orchestrator.py`** after receiving response
2. **Check `response` variable** - see raw LLM output
3. **Check `circuit_code`** after extraction
4. **Look for patterns:**
   ```python
   response.text.count('```python')  # Should be >= 2
   'import PySpice' in circuit_code  # LLM often adds this
   'circuit.Sinusoidal' in circuit_code  # Wrong syntax (should be SinusoidalVoltageSource)
   'in', 'out' as node names  # Python keywords
   ```

5. **Verify fixes applied** in `circuit_builder.py`:
   ```python
   # Check each fix was applied
   'SinusoidalVoltageSource' in filtered_code
   'input_node' in filtered_code  # If had 'in' originally
   'u_nF' in filtered_code  # If had u_uF
   ```

### Scenario 3: No Data Returned

**Symptoms:** Simulation runs but `results['data']` is None

**Debug Steps:**

1. **Set breakpoint** after simulation completes (~line ~290)
2. **Check `analysis` variable:**
   ```python
   analysis.frequency  # Should have values
   analysis['out']     # Output voltage at 'out' node
   len(analysis.frequency)  # Should be > 0
   ```
3. **Check results:**
   ```python
   results['data']
   results['plots']
   results['error']
   ```

**Common Issues:**
- No node named 'out' → LLM used different node name
- Wrong analysis type → Transient vs AC confusion
- Circuit has no path to ground → Floating node

---

## Logging for Debugging

### Enable Debugging Output

**In Streamlit Sidebar:**
- Set "LLM Debug: Show LLM debug info" ✓
- Check "Show raw LLM response" in UI

**In terminal:**
```python
# Add temporary print statements
print(f"DEBUG: circuit_code length = {len(circuit_code)}")
print(f"DEBUG: filtered_code contains SinusoidalVoltageSource = {'SinusoidalVoltageSource' in filtered_code}")
print(f"DEBUG: namespace keys = {list(namespace.keys())}")
```

### Check Application Logs

```powershell
# View Streamlit logs
# They appear in the integrated terminal while running

# Check debug directory
cd debug
python check_issues.py  # View recent issues
```

---

## Debugging Tips

### 1. Use Conditional Breakpoints

Right-click breakpoint → "Edit Breakpoint" → Add condition:

```python
# Only break when circuit_code is too long
len(circuit_code) > 5000

# Only break when error contains specific text
str(results.get('error', '')) and 'duplicate' in results['error'].lower()

# Only break on 10th iteration
i == 10
```

### 2. Log Points (New in VS Code)

Right-click gutter → "Add Log Point":

```python
# Execute and continue (don't pause)
"Filtered code length: {len(filtered_code)}"
"Analysis has {len(analysis.frequency)} data points"
```

### 3. Watch Expressions

Add to WATCH panel (left of DEBUG CONSOLE):

```python
filtered_code
namespace.keys()
results['error']
analysis.frequency[:5]  # First 5 elements
```

### 4. Exception Breakpoints

- Click the gear icon in Run & Debug
- Enable "Python: Exception Breakpoints"
- Check: "raise", "exception caught"

### 5. Debugging Streamlit State

Streamlit reruns on every interaction. To debug:

```python
# In app.py, add at top
import streamlit as st

if st.session_state.get('debug_mode', False):
    st.write("=== Session State ===")
    st.write(st.session_state)
```

---

## Performance Profiling

### Profile App Performance

Add to `app.py`:

```python
import cProfile
import pstats

# Wrap function to profile
def profile_simulation():
    # Your code here
    pass

# Run profile
profiler = cProfile.Profile()
profiler.enable()
profile_simulation()
profiler.disable()

# Print stats
stats = pstats.Stats(profiler)
stats.sort_stats('cumtime')
stats.print_stats(10)  # Top 10 functions
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named X"

**Solution:** Ensure VS Code is using correct Python interpreter:
- `Ctrl+Shift+P` → "Python: Select Interpreter"
- Choose `pyspice` environment

### Debugger Won't Start

**Check:**
1. Python debugger extension installed
2. `launch.json` has correct paths
3. No other Python processes blocking port 5678
4. Restart VS Code

### Breakpoints Not Hit

**Solutions:**
1. Verify you're debugging the right file (tab)
2. Check "justMyCode" setting (try False)
3. Ensure code path actually executes
4. Restart VS Code sometimes helps

---

## Debug Configurations Explained

### Available Configs

1. **"Streamlit: Run App"** - Simple run, basic debugging
2. **"Streamlit: Debug App"** - Full debug with logging
3. **"Python: Circuit Builder Test"** - Test circuit builder alone
4. **"Python: Ralph Fixer"** - Debug Ralph system
5. **"Python: Debug with Args"** - Custom script with arguments

### Quick Switch

Press `Ctrl+Shift+D` → Click dropdown → Select config → F5

---

## Advanced: Remote Debugging

Debug from another machine (e.g., running on server):

```json
{
    "name": "Python: Remote Attach",
    "type": "python",
    "request": "attach",
    "connect": {
        "host": "remote-server.com",
        "port": 5678
    },
    "pathMappings": [
        {
            "localRoot": "${workspaceFolder}",
            "remoteRoot": "/path/on/remote"
        }
    ]
}
```

---

## Summary Checklist

- [ ] VS Code installed
- [ ] Python debugger extension installed
- [ ] Correct interpreter selected (pyspice env)
- [ ] Breakpoints set at key locations
- [ ] Debug mode launched (F5)
- [ ] Inspector panels open (Variables, Watch, Call Stack)
- [ ] Streamlit running in browser
- [ ] Can step through code with F10/F11
- [ ] Debug console accessible

---

**Need Help?**
- Check VS Output panel (Terminal) for errors
- View .vscode/launch.json for config issues
- Test simpler script first to isolate problem

**Happy Debugging! 🐛**
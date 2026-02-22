# VS Code Debugging - Setup Complete ✅

## What Was Created

### 1. Debug Configuration (`.vscode/launch.json`)
5 debug configurations ready to use:
- `Streamlit: Run App` - Basic run
- `Streamlit: Debug App` - Full debug with logging
- `Python: Circuit Builder Test` - Test circuit builder alone
- `Python: Ralph Fixer` - Debug Ralph system
- `Python: Debug with Args` - Custom scripts

### 2. VS Code Settings (`.vscode/settings.json`)
- Python interpreter set to `pyspice` environment
- Auto-save and formatting enabled
- Hidden files configured

### 3. Documentation
- **`DEBUG_REFERENCE.md`** - Quick reference (2 min read) ⭐ START HERE
- **`docs/VS_CODE_DEBUGGING.md`** - Full debugging guide (10 min read)

---

## Quick Start (30 seconds)

### 1. Open in VS Code
```powershell
cd C:\Users\augus\.openclaw\workspace\llm-sim-poc
code .
```

### 2. Select Python Interpreter
- `Ctrl+Shift+P` → "Python: Select Interpreter"
- Choose: `C:\Users\augus\anaconda3\envs\pyspice\python.exe`

### 3. Start Debugging
- `Ctrl+Shift+D` (Debug View)
- Select: "Streamlit: Debug App"
- Press: `F5`

**Done!** App runs with breakpoints active.

---

## Common Debug Locations

**Circuit Building** (`circuit_builder.py`):
- Line 227: `run_simulation()` entry point
- Line 254: DC→Pulse conversion
- Line 278: LLM fixes (Sinusoidal → SinusoidalVoltageSource)
- Line 288: Before code execution

**LLM Calls** (`llm_orchestrator.py`):
- Line 120: Before API call
- Line 125: After response received

**Error Handling** (`error_handler.py`):
- Line 45: Error categorization

---

## What You Can Debug

1. **See filtered code** - What circuit code gets executed
2. **Check variables** - Inspect `filtered_code`, `namespace`, `analysis`
3. **Step through** - F10 (step over), F11 (step into)
4. **Test in console** - Run Python commands while paused

Example in Debug Console:
```python
filtered_code  # See the code
'input_node' in filtered_code  # Check if fix applied
len(analysis.frequency)  # Data points returned
results['error']  # See error message
```

---

## Keyboard Shortcuts

| Action | Key |
|--------|-----|
| Start/Continue | `F5` |
| Step Over | `F10` |
| Step Into | `F11` |
| Step Out | `Shift+F11` |
| Stop | `Shift+F5` |
| Toggle Breakpoint | `F9` |
| Debug View | `Ctrl+Shift+D` |
| Debug Console | `Ctrl+Shift+Y` |

---

## Troubleshooting

**"ModuleNotFoundError"** → Select correct interpreter (pyspice)
**Breakpoint not hit** → Restart VS Code
**No variables showing** → Ensure debug session active

---

## Documentation

**Quick:** `DEBUG_REFERENCE.md` (2 pages)
**Full:** `docs/VS_CODE_DEBUGGING.md` (complete guide)

---

**Happy Debugging! 🐛**

Start with the quick reference → Set a breakpoint → Start debugging!